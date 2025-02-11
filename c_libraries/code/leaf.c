#include "std.h"
#include "leaf.h"

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>


//HEAP ALLOCAITON

void __LEAF_HeapAllocation_constructor(struct __LEAF_HeapAllocation* self, void* data, size_t size, void(*destructorPointer)(void* self)){

    //pointer to the actual data
    self->data = data;

    //initialize other stuff
    self->size = size;
    __STD_List_constructor(&self->heapReferences, (void(*)(void*))&__LEAF_HeapVariable_destructor);
    self->scopeLevel = -1;
    self->destructorPointer = destructorPointer;   
}




void __LEAF_HeapAllocation_destructor(struct __LEAF_HeapAllocation* self){

    //CALL DESTRUCTOR ON THE OBJECT ITSELF
    self->destructorPointer(self->data);

    //FREE THE MALLOC'D SPACE FOR THE DATA
    free(self->data);
     
    //other cleanup (will not invoke any destructors since list has to be empty for this to be executing) (hopefully)
    __STD_List_destructor(&self->heapReferences);
}



void __LEAF_HeapAllocation_removeScopeLevel(struct __LEAF_HeapAllocation* self){

    //no need to inform the current level of the change since it is coming from that scope
    self->scopeLevel = -1;

    __LEAF_HeapAllocation_checkAutodestruction(self);
}


void __LEAF_HeapAllocation_removeHeapReference(struct __LEAF_HeapAllocation* self, struct __LEAF_HeapVariable* reference){

    __STD_List_silentlyRemoveByElement(&self->heapReferences, reference);
    __LEAF_HeapAllocation_checkAutodestruction(self);
}




void __LEAF_HeapAllocation_checkAutodestruction(struct __LEAF_HeapAllocation* self){

    if (self->heapReferences.size == 0 && self->scopeLevel == -1){
        __LEAF_HeapAllocation_destructor(self);
    }
}



//SCOPE STUFF



void __LEAF_Scope_constructor(struct __LEAF_Scope* self, int level){

    self->level = level;

    __STD_List_constructor(&self->heapVariables, (void(*)(void*))&__LEAF_HeapVariable_destructor);
    __STD_List_constructor(&self->stackDependentAllocations, (void(*)(void*))&__LEAF_HeapAllocation_destructor);
}


void __LEAF_Scope_destructor(struct __LEAF_Scope* self){

    //destruct all heap variables associated with the scope
    __STD_List_destructor(&self->heapVariables);

    //inform all allocations that rely on this stack level we are going out of scope + silently remove them from list
    for (int i=self->stackDependentAllocations.size-1; i>=0; i--){
        struct __LEAF_HeapAllocation* allocation = __STD_List_get(&self->stackDependentAllocations, (size_t)i);
        __LEAF_HeapAllocation_removeScopeLevel(allocation);

        __STD_List_silentRemoveByIndex(&self->stackDependentAllocations, (size_t)i);
    }

    //destroy the list (no danger of invoking destructors since we've erased it all)
    __STD_List_destructor(&self->stackDependentAllocations);
}



//VARIABLE STUFF


void __LEAF_HeapVariable_constructor(struct __LEAF_HeapVariable* self, struct __LEAF_HeapAllocation* allocation){

    //NOTE: dependents should not be destroyed until manually removed

    self->allocation = allocation;
    __STD_List_constructor(&self->dependents, (void(*)(void*))&__LEAF_HeapAllocation_destructor);
    __STD_List_add(&self->dependents, allocation);
}


void __LEAF_HeapVariable_destructor(struct __LEAF_HeapVariable* self){

    for (int i=self->dependents.size-1; i>=0; i--){
        struct __LEAF_HeapAllocation* dependent = __STD_List_get(&self->dependents, i);

        __LEAF_HeapAllocation_removeHeapReference(dependent, self);
        __STD_List_silentRemoveByIndex(&self->dependents, i);
    }

    __STD_List_destructor(&self->dependents);
}



//GENERIC "UTILITY" STUFF

void __LEAF_openScope(struct __STD_List* SCOPES){

    struct __LEAF_Scope* newScope = (struct __LEAF_Scope*)malloc(sizeof(struct __LEAF_Scope));
    __LEAF_Scope_constructor(newScope, SCOPES->size);

    __STD_List_add(SCOPES, newScope);
}


void __LEAF_initHeapVariable(struct __STD_List* SCOPES, struct __STD_List* HEAP_ALLOCATIONS, int source, void* object, size_t size, void(*destructorPointer)(void* self)){

    struct __LEAF_HeapAllocation* allocation;
    
    if (source == 0){
        //Variable comes from a constructor, is new and we need a new heap allocation
        //object is the pointer to the object itself
        allocation = (struct __LEAF_HeapAllocation*)malloc(sizeof(struct __LEAF_HeapAllocation));
        __LEAF_HeapAllocation_constructor(allocation, object, size, destructorPointer);
        __STD_List_add(HEAP_ALLOCATIONS, allocation);
    }

    else if (source == 1){
        //Variable comes from another heap allocation
        //object is the other allocation
        allocation = (struct __LEAF_HeapAllocation*)object;
    }

    else if (source == 2){
        //Variable comes from a stack allocation, we need to create the heapAllocation + malloc memory for a copy of the
        //stack object

        void* newObject = malloc(size);
        memcpy(newObject, object, size);//*(void*)newObject = *(void*)object;

        allocation = (struct __LEAF_HeapAllocation*)malloc(sizeof(struct __LEAF_HeapAllocation));
        __LEAF_HeapAllocation_constructor(allocation, newObject, size, destructorPointer);
        __STD_List_add(HEAP_ALLOCATIONS, allocation);
    }

    else{
        //ERROR
    }
    
    //INIT THE VARIABLE
    struct __LEAF_HeapVariable* heapVariable = (struct __LEAF_HeapVariable*)malloc(sizeof(struct __LEAF_HeapVariable));
    __LEAF_HeapVariable_constructor(heapVariable, allocation);

    //INFORM THE ALLOCATION THAT IT HAS A NEW REFERENCE
    __STD_List_add(&allocation->heapReferences, heapVariable);

    //PUT THE VARIABLE IN THE SCOPE
    struct __LEAF_Scope* currentScope = __STD_List_get(SCOPES, SCOPES->size - 1);
    __STD_List_add(&currentScope->heapVariables, heapVariable);
}



void __LEAF_closeScope(struct __STD_List* SCOPES, struct __STD_List* HEAP_ALLOCATIONS){

    // STEP 1, REMOVE THE SCOPE, WILL TRIGGER THE DESTRUCTOR IN THE VARIABLES
    __STD_List_removeByIndex(SCOPES, SCOPES->size - 1);


}



void __LEAF_voidDestructor(void* self){
    //DO NOTHING
}