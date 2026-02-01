; Comprehensive C# extraction query
; Captures: classes, methods, properties, interfaces, structs, enums, records
; with full metadata including modifiers, parameters, return types, inheritance

; ============================================================================
; TYPE DEFINITIONS
; ============================================================================

; Class declaration with inheritance
(class_declaration
  (modifier)* @modifier
  name: (identifier) @name
  type_parameters: (type_parameter_list)? @type_params
  (base_list
    (identifier) @extends)*
  body: (declaration_list) @body) @definition.class

; Interface declaration
(interface_declaration
  (modifier)* @modifier
  name: (identifier) @name
  type_parameters: (type_parameter_list)? @type_params
  (base_list
    (identifier) @extends)*
  body: (declaration_list) @body) @definition.interface

; Struct declaration
(struct_declaration
  (modifier)* @modifier
  name: (identifier) @name
  type_parameters: (type_parameter_list)? @type_params
  (base_list
    (identifier) @extends)*
  body: (declaration_list) @body) @definition.struct

; Enum declaration
(enum_declaration
  (modifier)* @modifier
  name: (identifier) @name
  (base_list
    (identifier) @extends)?
  body: (enum_member_declaration_list) @body) @definition.enum

; Record declaration (C# 9+)
(record_declaration
  (modifier)* @modifier
  name: (identifier) @name
  (parameter_list)? @params
  (base_list
    (identifier) @extends)*
  body: (declaration_list)? @body) @definition.record

; ============================================================================
; METHODS AND CONSTRUCTORS
; ============================================================================

; Method declaration with modifiers
(method_declaration
  (modifier)* @modifier
  returns: (_) @return_type
  name: (identifier) @name
  type_parameters: (type_parameter_list)? @type_params
  parameters: (parameter_list) @params
  body: [(block) (arrow_expression_clause)]? @body) @definition.method

; Constructor declaration
(constructor_declaration
  (modifier)* @modifier
  name: (identifier) @name
  parameters: (parameter_list) @params
  (constructor_initializer)? @initializer
  body: (block)? @body) @definition.constructor

; Destructor/Finalizer declaration
(destructor_declaration
  name: (identifier) @name
  parameters: (parameter_list) @params
  body: (block)? @body) @definition.destructor

; ============================================================================
; PROPERTIES AND FIELDS
; ============================================================================

; Property declaration
(property_declaration
  (modifier)* @modifier
  type: (_) @type
  name: (identifier) @name
  accessors: (accessor_list)? @accessors) @definition.property

; Field declaration
(field_declaration
  (modifier)* @modifier
  (variable_declaration
    type: (_) @type
    (variable_declarator
      name: (identifier) @name))) @definition.field

; Event field declaration
(event_field_declaration
  (modifier)* @modifier
  (variable_declaration
    type: (_) @type
    (variable_declarator
      name: (identifier) @name))) @definition.event

; ============================================================================
; PARAMETERS (for detailed method signature extraction)
; ============================================================================

; Regular parameter
(parameter
  (modifier)* @param.modifier
  type: (_) @param.type
  name: (identifier) @param.name
  (default_expression)? @param.default) @definition.parameter

; ============================================================================
; CONTROL FLOW PATTERNS (for characteristics)
; ============================================================================

; Try-catch-finally
(try_statement) @pattern.try_catch

; Catch clause specifically (to count catch blocks)
(catch_clause
  (catch_declaration
    type: (_) @catch.type
    name: (identifier)? @catch.name)?) @pattern.catch

; For loops
(for_statement) @pattern.loop

; Foreach loops
(foreach_statement) @pattern.loop

; While loops
(while_statement) @pattern.loop

; Do-while loops
(do_statement) @pattern.loop

; ============================================================================
; ASYNC PATTERNS
; ============================================================================

; Await expressions
(await_expression) @pattern.async

; ============================================================================
; LINQ PATTERNS
; ============================================================================

; Query expressions (LINQ syntax)
(query_expression) @pattern.linq

; From clause
(from_clause) @pattern.linq.from

; Where clause
(where_clause) @pattern.linq.where

; Select clause
(select_clause) @pattern.linq.select

; ============================================================================
; CALL PATTERNS
; ============================================================================

; Method invocation (direct call)
(invocation_expression
  function: (identifier) @call.name) @pattern.call

; Method invocation (member access like obj.Method())
(invocation_expression
  function: (member_access_expression
    expression: (_) @call.target
    name: [(identifier) (generic_name (identifier))] @call.name)) @pattern.call

; Object creation (new expressions)
(object_creation_expression
  type: (_) @create.type) @pattern.new

; ============================================================================
; EXCEPTION PATTERNS
; ============================================================================

; Throw statement
(throw_statement) @pattern.throw

; Throw expression (C# 7+)
(throw_expression) @pattern.throw

; ============================================================================
; RETURN PATTERNS
; ============================================================================

; Return statement
(return_statement) @pattern.return

; Yield return
(yield_statement) @pattern.yield

; ============================================================================
; USING/RESOURCE PATTERNS (I/O detection)
; ============================================================================

; Using statement (traditional)
(using_statement) @pattern.using

; Using directive (imports)
(using_directive
  (identifier) @using.namespace) @pattern.using_directive

(using_directive
  (qualified_name) @using.namespace) @pattern.using_directive

; Local using declaration (C# 8+, e.g., "using var stream = ...")
; Matches the "using" keyword in local declarations
(local_declaration_statement) @pattern.using_local

; ============================================================================
; MODIFIER PATTERNS (for access level and characteristic detection)
; ============================================================================

; Capture specific modifiers for analysis
(modifier) @modifier.any

; ============================================================================
; ATTRIBUTE PATTERNS
; ============================================================================

; Attribute lists (decorators in C#)
(attribute_list
  (attribute
    name: (_) @attribute.name)) @pattern.attribute

; ============================================================================
; LAMBDA AND DELEGATE PATTERNS
; ============================================================================

; Lambda expression with parameter list
(lambda_expression
  parameters: (parameter_list) @lambda.params) @pattern.lambda

; Lambda expression with implicit parameter (single identifier)
(lambda_expression
  parameters: (implicit_parameter) @lambda.params) @pattern.lambda

; Lambda expression (catch-all)
(lambda_expression) @pattern.lambda

; Anonymous method expression
(anonymous_method_expression) @pattern.anonymous_method

; ============================================================================
; NULL SAFETY PATTERNS
; ============================================================================

; Null conditional access (?. operator)
(conditional_access_expression) @pattern.null_conditional

; Null coalescing (?? operator) - binary expression with null on left
(binary_expression
  left: (null_literal)) @pattern.null_coalescing

; ============================================================================
; ADDITIONAL PATTERNS
; ============================================================================

; Switch expression (C# 8+)
(switch_expression) @pattern.switch_expression

; Switch statement
(switch_statement) @pattern.switch

; Lock statement
(lock_statement) @pattern.lock

; Checked/unchecked
(checked_statement) @pattern.checked
(checked_expression) @pattern.checked

; Fixed statement (for unsafe pointer operations)
(fixed_statement) @pattern.fixed

; Unsafe block
(unsafe_statement) @pattern.unsafe

; Interpolated string (for string analysis)
(interpolated_string_expression) @pattern.interpolated_string

; Nameof expression
(invocation_expression
  function: (identifier) @_nameof
  (#eq? @_nameof "nameof")) @pattern.nameof

; Typeof expression
(typeof_expression) @pattern.typeof

; Is pattern expression
(is_pattern_expression) @pattern.is_pattern

; As expression
(as_expression) @pattern.as_cast

; Cast expression
(cast_expression) @pattern.cast
