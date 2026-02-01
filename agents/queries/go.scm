; Comprehensive Go extraction query
; Captures: functions, methods, types, structs, interfaces, with full metadata
; Go-specific patterns: receivers, multiple return values, channels, goroutines

; ==============================================================================
; DEFINITIONS - Functions and Methods
; ==============================================================================

; Regular function declaration (exported if capitalized name)
(function_declaration
  name: (identifier) @name
  parameters: (parameter_list) @params
  result: [
    (type_identifier)
    (qualified_type)
    (pointer_type)
    (slice_type)
    (map_type)
    (channel_type)
    (parameter_list)
  ]? @return_type
  body: (block) @body) @definition.function

; Method declaration with receiver
(method_declaration
  receiver: (parameter_list
    (parameter_declaration
      name: (identifier)? @receiver.name
      type: [
        (type_identifier) @receiver.type
        (pointer_type
          (type_identifier) @receiver.type) @receiver.pointer
      ])) @receiver
  name: (field_identifier) @name
  parameters: (parameter_list) @params
  result: [
    (type_identifier)
    (qualified_type)
    (pointer_type)
    (slice_type)
    (map_type)
    (channel_type)
    (parameter_list)
  ]? @return_type
  body: (block) @body) @definition.method

; ==============================================================================
; DEFINITIONS - Types
; ==============================================================================

; Struct type declaration
(type_declaration
  (type_spec
    name: (type_identifier) @name
    type: (struct_type
      (field_declaration_list) @fields))) @definition.struct

; Interface type declaration
(type_declaration
  (type_spec
    name: (type_identifier) @name
    type: (interface_type) @interface_body)) @definition.interface

; Type alias
(type_declaration
  (type_spec
    name: (type_identifier) @name
    type: (type_identifier) @alias_type)) @definition.type_alias

; Generic type alias (slice, map, pointer, etc.)
(type_declaration
  (type_spec
    name: (type_identifier) @name
    type: [
      (slice_type)
      (map_type)
      (pointer_type)
      (channel_type)
      (function_type)
    ] @type_value)) @definition.type

; ==============================================================================
; GO-SPECIFIC PATTERNS - Concurrency
; ==============================================================================

; Goroutine (go keyword)
(go_statement
  (call_expression
    function: [
      (identifier) @goroutine.function
      (selector_expression
        field: (field_identifier) @goroutine.function)
      (func_literal)
    ])) @pattern.goroutine

; Channel operations - send
(send_statement
  channel: (_) @channel.name) @pattern.channel_send

; Channel operations - receive (standalone)
(receive_statement) @pattern.channel_receive

; Channel receive in expression
(unary_expression
  operator: "<-"
  operand: (_) @channel.name) @pattern.channel_receive

; Select statement (channel multiplexing)
(select_statement) @pattern.select

; ==============================================================================
; GO-SPECIFIC PATTERNS - Error Handling
; ==============================================================================

; Defer statement
(defer_statement
  (call_expression
    function: [
      (identifier) @defer.function
      (selector_expression
        field: (field_identifier) @defer.function)
      (func_literal)
    ])) @pattern.defer

; Panic call
(call_expression
  function: (identifier) @_panic
  (#eq? @_panic "panic")) @pattern.panic

; Recover call
(call_expression
  function: (identifier) @_recover
  (#eq? @_recover "recover")) @pattern.recover

; Common error check pattern: if err != nil
(if_statement
  condition: (binary_expression
    left: (identifier) @_err
    operator: "!="
    right: (nil))
  (#eq? @_err "err")) @pattern.error_check

; Short variable declaration with error (common pattern: x, err := ...)
(short_var_declaration
  left: (expression_list
    (identifier)
    (identifier) @_err)
  (#eq? @_err "err")) @pattern.error_assignment

; ==============================================================================
; CONTROL FLOW PATTERNS
; ==============================================================================

; For loop (Go's only loop construct)
(for_statement) @pattern.loop

; For-range loop
(for_statement
  (range_clause)) @pattern.range_loop

; If statement
(if_statement) @pattern.conditional

; If with initializer (common Go pattern: if err := ...; err != nil)
(if_statement
  initializer: (_)) @pattern.conditional_init

; Switch statement (expression switch)
(expression_switch_statement) @pattern.switch

; Type switch statement
(type_switch_statement) @pattern.type_switch

; ==============================================================================
; CALL PATTERNS
; ==============================================================================

; Function call (identifier)
(call_expression
  function: (identifier) @call.name) @pattern.call

; Method call (selector expression)
(call_expression
  function: (selector_expression
    operand: (_) @call.receiver
    field: (field_identifier) @call.name)) @pattern.call

; ==============================================================================
; RETURN PATTERNS
; ==============================================================================

; Return statement
(return_statement) @pattern.return

; Return with multiple values
(return_statement
  (expression_list
    (_)
    (_)+)) @pattern.return_multiple

; Return nil (common error pattern)
(return_statement
  (expression_list
    (nil))) @pattern.return_nil

; ==============================================================================
; FUNCTION LITERALS (closures)
; ==============================================================================

; Anonymous function / closure
(func_literal
  parameters: (parameter_list) @closure.params
  result: [
    (type_identifier)
    (qualified_type)
    (pointer_type)
    (parameter_list)
  ]? @closure.return_type
  body: (block) @closure.body) @pattern.closure

; ==============================================================================
; TYPE ASSERTIONS AND CONVERSIONS
; ==============================================================================

; Type assertion: x.(Type)
(type_assertion_expression
  type: (_) @assertion.type) @pattern.type_assertion

; ==============================================================================
; COMPOSITE LITERALS (struct/slice/map instantiation)
; ==============================================================================

; Struct literal
(composite_literal
  type: (type_identifier) @literal.type
  body: (literal_value)) @pattern.composite_literal

; Slice literal
(composite_literal
  type: (slice_type) @literal.type
  body: (literal_value)) @pattern.slice_literal

; Map literal
(composite_literal
  type: (map_type) @literal.type
  body: (literal_value)) @pattern.map_literal

; ==============================================================================
; MAKE AND NEW (allocation)
; ==============================================================================

; make() call - slices, maps, channels
(call_expression
  function: (identifier) @_make
  arguments: (argument_list
    (_) @make.type)
  (#eq? @_make "make")) @pattern.make

; new() call - pointer allocation
(call_expression
  function: (identifier) @_new
  arguments: (argument_list
    (_) @new.type)
  (#eq? @_new "new")) @pattern.new

; ==============================================================================
; VARIADIC PARAMETERS
; ==============================================================================

; Variadic parameter declaration
(variadic_parameter_declaration
  name: (identifier) @variadic.name
  type: (_) @variadic.type) @pattern.variadic_param

; Spread operator in call
(call_expression
  arguments: (argument_list
    (variadic_argument))) @pattern.spread_call

; ==============================================================================
; BLANK IDENTIFIER (intentional ignore)
; ==============================================================================

; Blank identifier in short var declaration (deliberately ignoring a value)
((short_var_declaration
  left: (expression_list
    (identifier) @pattern.blank_identifier))
  (#eq? @pattern.blank_identifier "_"))

; Blank identifier in range clause
((range_clause
  left: (expression_list
    (identifier) @pattern.blank_identifier))
  (#eq? @pattern.blank_identifier "_"))

; Blank identifier in assignment
((assignment_statement
  left: (expression_list
    (identifier) @pattern.blank_identifier))
  (#eq? @pattern.blank_identifier "_"))
