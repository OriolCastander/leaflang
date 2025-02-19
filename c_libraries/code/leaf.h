/**
 Constructions and functions used in the transpiling of leaflang into c.

 Oriol Castander

 */
#ifndef LEAF_H
#define LEAF_H

#include "./std.h"

//STRUCTS

/**
 * Holds a pointer to the malloc'd address of data stored in the heap, along with
 * a list references in use of that data (so that when all are gone, the data is freed)
 */
struct __LEAF_HeapAllocation{

    /** Pointer to the heap address with the actual data */
    void* data;

    /** Size of the allocated thing (sizeof(bla bla bla)) */
    size_t size;

    /** List<HeapVariable>. List of references that reference this data */
    struct __STD_List heapReferences;

    /**
     * Scope level of the heap allocation. -1 means no stack allocated variables hold a reference to the allocation
     * a different number means that the scope at that level has at least 1 variable with "ties" to this allocation.
     */
    int scopeLevel;

    /** Destructor of the internal object */
    void(*destructorPointer)(void* self);

};


/**
 * A scope is anyting between curly braces (function, if block...).
 * Contains heap variables that go out of scope (and the reference count of the allocations must decrease)
 * 
 */
struct __LEAF_Scope{

    /** Scope level (also index in SCOPES) */
    int level;

    /** List<HeapVariable> of heap inited variables in this scope (will be destructed when scope closes) */
    struct __STD_List heapVariables;

    /** List<HeapAllocation> List of allocations that hold this level as their scope level, and need to be 
     * informed of level closure when scope goes out of scope
    */
    struct __STD_List stackDependentAllocations;

};


/** Data about a heap allocated variable */
struct __LEAF_HeapVariable{

    /** Pointer to the allocation with the actual data */
    struct __LEAF_HeapAllocation* allocation;

    /** List<HeapAllocation> Allocations that will not be freed until this variable is deleted */
    struct __STD_List dependents;
};




//HEAP ALLOCATION

/**
 * Constructor of the heap allocation. Holds a pointer (called data) to the actual memory with the data (previously allocated)
 */
void __LEAF_HeapAllocation_constructor(struct __LEAF_HeapAllocation* self, void* data, size_t size, void(*destructorPointer)(void* self));


/**
 * Destructor of the heap allocation, calls the destructor on the object and also frees the malloc
 */
void __LEAF_HeapAllocation_destructor(struct __LEAF_HeapAllocation* self);

/**
 * Sets the scopeLevel = -1, checks for autodestruction.
 * Should be called from the scope object when it is being destroyed, since it does not inform anyone of anything
 * like changeScopeLevel
 */
void __LEAF_HeapAllocation_removeScopeLevel(struct __LEAF_HeapAllocation* self);


/**
 * Silently (without invoking the destructor) removes a reference from heapReferences and checks for autodestruction
 */
void __LEAF_HeapAllocation_removeHeapReference(struct __LEAF_HeapAllocation* self, struct __LEAF_HeapVariable* reference);


/**
 * Calls the destructor if no heap references and scope level is -1
 */
void __LEAF_HeapAllocation_checkAutodestruction(struct __LEAF_HeapAllocation* self);





//SCOPE


/**
 * Scope constructor
 */
void __LEAF_Scope_constructor(struct __LEAF_Scope* self, int level);


/**
 * Destructs the scope. Destructs all the heap variables that go out of scope, and informs the stack dependent
 * allocations that the scope is going "out of scope"
 */
void __LEAF_Scope_destructor(struct __LEAF_Scope* self);






//VARIABLES


/** Constructor */
void __LEAF_HeapVariable_constructor(struct __LEAF_HeapVariable* self, struct __LEAF_HeapAllocation* allocation);



void __LEAF_HeapVariable_destructor(struct __LEAF_HeapVariable* self); //TODO_U




//"UTILITY" ALL ROUNDER FUNCTIONS

/** Creates a scope and appends it to the list
 * Debug level 0: No debug
 * Debug level 1: Prints the opening of the scope
*/
void __LEAF_openScope(struct __STD_List* SCOPES, int debugLevel);

/**
 * Inits a heap variable, creates the allocation for it if needed, and adds it to the scope.
 * Source is 0 if Variable comes from a constructor, 1 if variable comes from another heap allocated thing and 2 if it
 * comes from a stack allocated thing. To improve with an info array
 */
void __LEAF_initHeapVariable(struct __STD_List* SCOPES, struct __STD_List* HEAP_ALLOCATIONS, int source, void* object, size_t size, void(*destructorPointer)(void* self));

/**
 * Destroys the scope
 * Debug level 0: No debug
 * Debug level 1: Prints the closing of the scope
 */
void __LEAF_closeScope(struct __STD_List* SCOPES, struct __STD_List* HEAP_ALLOCATIONS, int debugLevel);



/**
 * Void destructor that does nothing. Can be passed to stuff that needs a destructor but nothing needs to be done
 */
void __LEAF_voidDestructor(void* self);

#endif //LEAF_H