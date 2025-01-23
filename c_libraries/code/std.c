#include "std.h"

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>


void __STD_List_constructor(struct __STD_List* self, void(*destructorPointer)(void* self)){


    size_t initialCapacity = 5;
    self->array = (void**)malloc(initialCapacity * sizeof(void*));
    self->size = 0;
    self->capacity = initialCapacity;
    self->destructorPointer = destructorPointer;
}


void __STD_List_destructor(struct __STD_List* self){


    //CALL THE DESTRUCTORS ON ALL THE ELEMENTS
    for (int i=0; i<self->size; i++){
        self->destructorPointer(self->array[(size_t)i]);
    }
    free(self->array);
}



void __STD_List_add(struct __STD_List* self, void* element){

    if (self->size == self->capacity){ //REALLOC IF NEEDED
        self->capacity *= 2;
        self->array = (void**)realloc(self->array, self->size * sizeof(void*));
    }

    self->array[self->size] = element;
    self->size += 1;
}


void* __STD_List_get(struct __STD_List* self, size_t index){

    if (index >= self->size){
        //TODO: ERROR HERE MY FRIEND
    }

    return self->array[index];
}


void __STD_List_removeByIndex(struct __STD_List* self, int index){
    
    if (index < 0 || (size_t)index >= self->size){
        //TODO: ERROR HERE MY FRIEND
        return;
    }

    //call the destructor on the removed element
    self->destructorPointer(self->array[(size_t)index]);

    //shift all elements to the left by one from the elementIndex forwards
    for (int i=index + 1; i<self->size; i++){
        self->array[i-1] = self->array[(size_t)i];
    }

    self->size -= 1;
}



void __STD_List_removeByElement(struct __STD_List* self, void* element){
    
    for (int i=0; i<self->size; i++){
        if (self->array[i] == element){
            __STD_List_removeByIndex(self, i);
        }
    }

    //TODO: NO ELEMENT
}



void __STD_List_silentRemoveByIndex(struct __STD_List* self, int index){
    
    if (index < 0 || (size_t)index >= self->size){
        //TODO: ERROR HERE MY FRIEND
        return;
    }

    //shift all elements to the left by one from the elementIndex forwards
    for (int i=index + 1; i<self->size; i++){
        self->array[i-1] = self->array[i];
    }

    self->size -= 1;
}



void __STD_List_silentlyRemoveByElement(struct __STD_List* self, void* element){
    
    for (int i=0; i<self->size; i++){
        if (self->array[i] == element){
            __STD_List_silentRemoveByIndex(self, i);
        }
    }

    //TODO: NO ELEMENT
}