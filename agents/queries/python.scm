; Comprehensive Python extraction query
; Captures: functions, methods, classes, with full metadata

; Function definition with decorators
(decorated_definition
  (decorator) @decorator
  definition: (function_definition
    name: (identifier) @name
    parameters: (parameters) @params
    return_type: (type)? @return_type
    body: (block) @body)) @definition.function.decorated

; Regular function definition
(function_definition
  name: (identifier) @name
  parameters: (parameters) @params
  return_type: (type)? @return_type
  body: (block) @body) @definition.function

; Async function definition
(function_definition
  "async" @async_keyword
  name: (identifier) @name
  parameters: (parameters) @params
  body: (block) @body) @definition.function.async

; Class definition
(class_definition
  name: (identifier) @name
  superclasses: (argument_list
    (identifier) @extends)?
  body: (block) @body) @definition.class

; Method definition (inside class)
(class_definition
  body: (block
    (function_definition
      name: (identifier) @name
      parameters: (parameters) @params
      body: (block) @body) @definition.method))

; ---- Control flow patterns ----

; Try-except
(try_statement) @pattern.try_catch

; Loops
(for_statement) @pattern.loop
(while_statement) @pattern.loop

; List/dict/set comprehensions (implicit loops)
(list_comprehension) @pattern.loop
(dictionary_comprehension) @pattern.loop
(set_comprehension) @pattern.loop
(generator_expression) @pattern.loop

; Await expressions
(await) @pattern.async

; Function calls
(call
  function: [
    (identifier) @call.name
    (attribute
      attribute: (identifier) @call.name)
  ]) @pattern.call

; Raise statements
(raise_statement) @pattern.throw

; Return statements
(return_statement) @pattern.return

; With statements (context managers - often I/O)
(with_statement) @pattern.context_manager
