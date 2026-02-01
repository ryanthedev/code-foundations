; Comprehensive TypeScript/JavaScript extraction query
; Captures: functions, methods, classes, with full metadata

; Exported async function with parameters and return type
(export_statement
  declaration: (function_declaration
    name: (identifier) @name
    parameters: (formal_parameters) @params
    return_type: (type_annotation)? @return_type
    body: (statement_block) @body)) @definition.function.exported.async

; Regular function declaration
(function_declaration
  name: (identifier) @name
  parameters: (formal_parameters) @params
  return_type: (type_annotation)? @return_type
  body: (statement_block) @body) @definition.function

; Arrow function assigned to variable
(lexical_declaration
  (variable_declarator
    name: (identifier) @name
    value: (arrow_function
      parameters: (formal_parameters) @params
      return_type: (type_annotation)? @return_type
      body: (_) @body))) @definition.function.arrow

; Class declaration
(class_declaration
  name: (type_identifier) @name
  (class_heritage
    (extends_clause
      value: (identifier) @extends))?
  (class_heritage
    (implements_clause
      (type_identifier) @implements))?
  body: (class_body) @body) @definition.class

; Exported class
(export_statement
  declaration: (class_declaration
    name: (type_identifier) @name
    body: (class_body) @body)) @definition.class.exported

; Method definition in class
(method_definition
  name: (property_identifier) @name
  parameters: (formal_parameters) @params
  return_type: (type_annotation)? @return_type
  body: (statement_block) @body) @definition.method

; Interface declaration
(interface_declaration
  name: (type_identifier) @name
  body: (interface_body) @body) @definition.interface

; Type alias
(type_alias_declaration
  name: (type_identifier) @name
  value: (_) @type_value) @definition.type

; ---- Control flow patterns (for characteristics) ----

; Try-catch
(try_statement) @pattern.try_catch

; For loops
(for_statement) @pattern.loop
(for_in_statement) @pattern.loop
(while_statement) @pattern.loop
(do_statement) @pattern.loop

; Await expressions
(await_expression) @pattern.async

; Call expressions (to track what functions are called)
(call_expression
  function: [
    (identifier) @call.name
    (member_expression
      property: (property_identifier) @call.name)
  ]) @pattern.call

; Throw statements
(throw_statement) @pattern.throw

; Return statements
(return_statement) @pattern.return
