; Comprehensive Swift extraction query
; Captures: classes, structs, enums, protocols, extensions, functions, properties
; with full modifiers, parameters, return types, and control flow patterns

; ============================================================================
; TYPE DEFINITIONS
; ============================================================================

; Class declaration
(class_declaration
  declaration_kind: "class"
  name: (type_identifier) @name
  (inheritance_specifier
    inherits_from: (user_type
      (type_identifier) @extends))?
  (modifiers)? @modifiers
  body: (class_body) @body) @definition.class

; Struct declaration
(class_declaration
  declaration_kind: "struct"
  name: (type_identifier) @name
  (inheritance_specifier
    inherits_from: (user_type
      (type_identifier) @implements))?
  (modifiers)? @modifiers
  body: (class_body) @body) @definition.struct

; Enum declaration
(class_declaration
  declaration_kind: "enum"
  name: (type_identifier) @name
  (inheritance_specifier
    inherits_from: (user_type
      (type_identifier) @implements))?
  (modifiers)? @modifiers
  body: (enum_class_body) @body) @definition.enum

; Protocol declaration
(protocol_declaration
  name: (type_identifier) @name
  (inheritance_specifier
    inherits_from: (user_type
      (type_identifier) @extends))?
  (modifiers)? @modifiers
  body: (protocol_body) @body) @definition.protocol

; Extension declaration
(class_declaration
  declaration_kind: "extension"
  name: (type_identifier) @name
  (inheritance_specifier
    inherits_from: (user_type
      (type_identifier) @implements))?
  body: (_) @body) @definition.extension

; Actor declaration
(class_declaration
  declaration_kind: "actor"
  name: (type_identifier) @name
  (inheritance_specifier
    inherits_from: (user_type
      (type_identifier) @implements))?
  (modifiers)? @modifiers
  body: (class_body) @body) @definition.actor

; ============================================================================
; FUNCTION DEFINITIONS
; ============================================================================

; Regular function declaration with all metadata
(function_declaration
  (modifiers)? @modifiers
  name: (simple_identifier) @name
  (parameter)* @params
  (throws)? @throws
  return_type: (_)? @return_type
  body: (function_body) @body) @definition.function

; Async function (when modifiers contains async)
(function_declaration
  (modifiers
    (function_modifier) @_async_mod)
  name: (simple_identifier) @name
  body: (function_body) @body
  (#match? @_async_mod "async")) @definition.function.async

; Init declaration (constructor)
(init_declaration
  (modifiers)? @modifiers
  (parameter)* @params
  (throws)? @throws
  body: (function_body) @body) @definition.init

; Failable init (init? or init!)
(init_declaration
  (bang)? @failable
  body: (function_body) @body) @definition.init.failable

; Deinit declaration (destructor)
(deinit_declaration
  body: (function_body) @body) @definition.deinit

; Protocol function declaration (no body)
(protocol_function_declaration
  name: (simple_identifier) @name
  (parameter)* @params
  (throws)? @throws
  return_type: (_)? @return_type) @definition.function.protocol

; Subscript declaration
(subscript_declaration
  (modifiers)? @modifiers
  (parameter)* @params
  return_type: (_)? @return_type) @definition.subscript

; ============================================================================
; PROPERTY DEFINITIONS
; ============================================================================

; Stored property (let/var)
(property_declaration
  (modifiers)? @modifiers
  (value_binding_pattern) @binding
  name: (pattern
    (simple_identifier) @name)
  (type_annotation)? @type
  value: (_)? @value) @definition.property

; Computed property (has computed_value)
(property_declaration
  name: (pattern
    (simple_identifier) @name)
  (type_annotation)? @type
  computed_value: (computed_property) @computed) @definition.property.computed

; Property with willSet/didSet observers
(property_declaration
  name: (pattern
    (simple_identifier) @name)
  (willset_didset_block) @observers) @definition.property.observed

; Protocol property declaration
(protocol_property_declaration
  name: (pattern
    (simple_identifier) @name)
  (type_annotation)? @type) @definition.property.protocol

; ============================================================================
; PARAMETERS (for detailed function signature extraction)
; ============================================================================

; Function parameter with external and internal name
(parameter
  external_name: (simple_identifier)? @param.external
  name: (simple_identifier) @param.name
  type: (_) @param.type) @definition.parameter

; ============================================================================
; MODIFIERS (for visibility and access analysis)
; ============================================================================

; Visibility modifiers (public, private, internal, fileprivate, open)
(modifiers
  (visibility_modifier) @modifier.visibility)

; Member modifiers (static, class)
(modifiers
  (member_modifier) @modifier.member)

; Function modifiers (async, mutating, nonmutating)
(modifiers
  (function_modifier) @modifier.function)

; Inheritance modifiers (final, override)
(modifiers
  (inheritance_modifier) @modifier.inheritance)

; Property modifiers (lazy)
(modifiers
  (property_modifier) @modifier.property)

; Mutation modifiers (mutating, nonmutating)
(modifiers
  (mutation_modifier) @modifier.mutation)

; Standalone modifier captures
(visibility_modifier) @modifier.visibility.standalone
(member_modifier) @modifier.member.standalone
(inheritance_modifier) @modifier.inheritance.standalone

; ============================================================================
; CONTROL FLOW PATTERNS (for characteristics)
; ============================================================================

; Do-catch blocks (Swift's try-catch)
(do_statement) @pattern.try_catch

; Catch block
(catch_block
  error: (_)? @catch.binding) @pattern.catch

; For-in loops
(for_statement
  item: (_) @loop.variable
  collection: (_) @loop.collection) @pattern.loop.for_in

; While loops
(while_statement
  condition: (_)? @loop.condition) @pattern.loop.while

; Repeat-while loops (do-while equivalent)
(repeat_while_statement
  condition: (_)? @loop.condition) @pattern.loop.repeat_while

; Guard statements (early exit)
(guard_statement
  condition: (_)? @guard.condition) @pattern.guard

; If statements
(if_statement) @pattern.if

; Switch statements
(switch_statement) @pattern.switch

; Switch entry (case)
(switch_entry) @pattern.switch.case

; ============================================================================
; ASYNC/AWAIT PATTERNS
; ============================================================================

; Await expressions
(await_expression) @pattern.async.await

; Async keyword in function modifiers
((function_modifier) @pattern.async.modifier
  (#match? @pattern.async.modifier "async"))

; ============================================================================
; ERROR HANDLING PATTERNS
; ============================================================================

; Try expressions (try, try?, try!)
(try_expression
  expr: (_)? @try.expression) @pattern.try

; Try operator keyword
(try_operator) @pattern.try.operator

; Throw keyword
(throw_keyword) @pattern.throw

; Throws modifier on functions
(throws) @pattern.throws

; ============================================================================
; CLOSURE PATTERNS
; ============================================================================

; Lambda/closure literals
(lambda_literal
  captures: (_)? @closure.captures
  (statements)? @closure.body) @pattern.closure

; Trailing closure in call
(call_expression
  (call_suffix
    (lambda_literal) @trailing_closure)) @pattern.call.with_closure

; ============================================================================
; FUNCTION CALLS
; ============================================================================

; Direct function call: foo()
(call_expression
  (simple_identifier) @call.name) @pattern.call

; Method call via navigation: obj.method()
(call_expression
  (navigation_expression
    (navigation_suffix
      (simple_identifier) @call.name))) @pattern.call.method

; Constructor call: Type.init() or Type()
(call_expression
  (constructor_expression)) @pattern.call.constructor

; Chained navigation (property access, method chaining)
(navigation_expression
  target: (_) @navigation.target
  suffix: (navigation_suffix
    (simple_identifier) @navigation.member)) @pattern.navigation

; ============================================================================
; RETURN STATEMENTS
; ============================================================================

; Return keyword
"return" @pattern.return

; ============================================================================
; OPTIONAL PATTERNS
; ============================================================================

; Optional type annotation (Type?)
(optional_type
  wrapped: (_) @optional.wrapped) @pattern.optional.type

; Force unwrap (value!)
(bang) @pattern.optional.force_unwrap

; Nil coalescing (value ?? default)
(nil_coalescing_expression) @pattern.optional.coalescing

; Nil literal
"nil" @pattern.nil

; Optional chaining operator
"?" @pattern.optional.chaining

; ============================================================================
; ATTRIBUTE PATTERNS
; ============================================================================

; Attributes (@main, @available, @objc, @escaping, etc.)
(attribute
  (user_type
    (type_identifier) @attribute.name)) @pattern.attribute

; Common attributes for detection
((attribute
  (user_type
    (type_identifier) @_attr_name))
  (#match? @_attr_name "^(available|objc|main|escaping|discardableResult|MainActor|Sendable)$")) @pattern.attribute.common

; ============================================================================
; IMPORT STATEMENTS
; ============================================================================

(import_declaration) @pattern.import

; ============================================================================
; TYPE CASTING PATTERNS
; ============================================================================

; As expression (type casting)
(as_expression) @pattern.cast.as

; Is check (type checking) - uses check_expression
(check_expression) @pattern.cast.is

; ============================================================================
; ENUM PATTERNS
; ============================================================================

; Enum entry (case)
(enum_entry) @pattern.enum.case

; ============================================================================
; MACRO PATTERNS
; ============================================================================

; Macro invocation (Swift 5.9+)
(macro_invocation) @pattern.macro

; ============================================================================
; SPECIAL LITERALS
; ============================================================================

; Special literals (#file, #line, #function, etc.)
(special_literal) @pattern.special_literal

; Directive (#if, #elseif, #else, #endif)
(directive) @pattern.directive

; Diagnostic (#warning, #error)
(diagnostic) @pattern.diagnostic
