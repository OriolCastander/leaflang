/**
 Definitions for the standard library of the leaflang programming language.
 These are purely c, and do not rely on any constructs of the language

 Oriol Castander
 */

#ifndef STD_H
#define STD_H

#include <stdlib.h>



///LIST

/**
 * The typical dynamic list, where sized is doubled when capacity is reached
 */
struct __STD_List{
    
    /** Pointer to the first element of the list */
    void** array;

    /** Current size of the list */
    size_t size;

    /** Capacity of the list */
    size_t capacity;

    /** Pointer to the destructor function of the object.
     * Applied to each element of the list when destructed, to one element when it is removed
     */
    void(*destructorPointer)(void* self);

};

/**
 * Constructor
 */
void __STD_List_constructor(struct __STD_List* self, void(*destructorPointer)(void* self));


/**
 * Frees everything
 */
void __STD_List_destructor(struct __STD_List* self);


/**
 * Adds element to the list, reallocs if needed
 */
void __STD_List_add(struct __STD_List* self, void* element);

/**
 * Gets the element at the index
 */
void* __STD_List_get(struct __STD_List* self, size_t index);


/**
 * Removes element at index index.
 * Index by int or size_t? currently index for compatibility stuff w/ leaflang
 */
void __STD_List_removeByIndex(struct __STD_List* self, int index);


/**
 * Removes the specified element
 */
void __STD_List_removeByElement(struct __STD_List* self, void* element);


/**
 * Like the remove by index, without invoking the destructor
 */
void __STD_List_silentRemoveByIndex(struct __STD_List* self, int index);


/**
 * List remove by element, without invoking the destructor
 */
void __STD_List_silentlyRemoveByElement(struct __STD_List* self, void* element);


#endif //STD_H