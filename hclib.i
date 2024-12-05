/******************************************************************************/
/* File:  hclib.i                                                            */
/******************************************************************************/
/* (C) Stefan C. Kremer, 2024                                                 */
/* A swig file to interface Python with the hclib library used for CIS*2750, */
/* Fall 2024.                                                               */
/******************************************************************************/

/* based on phylib.c and phylib.h */
%module hclib
%{
  #include "hclib.h"
%}

/******************************************************************************/

%include "hclib.h"

/******************************************************************************/
/* this creates a phylib_coord class in the phylib python module              */
/******************************************************************************/

%extend exboard_t {

  /* constructor method */
  exboard_t()
  {
    exboard_t *new;
    new = newboard();
    return  new;
  }

  char *__str__()
  {
    return stringboard( $self );
  }

  /* destructor method */
  ~exboard_t()
  {
    free( $self );
  }
};
