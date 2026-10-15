/**
 * Original teaching model. No target-module imports, native calls, network, or shell.
 * It intentionally validates more strictly than the observed conversion path.
 */
export function validate(schema, value, defs = {}, path = '$') {
  if (schema.$ref) {
    const name = schema.$ref.replace(/^#\/\$defs\//, '');
    if (!Object.hasOwn(defs, name)) return [`${path}: unresolved schema reference ${name}`];
    return validate(defs[name], value, defs, path);
  }
  const errors = [];
  const match = type => ({
    null: value === null,
    object: value !== null && typeof value === 'object' && !Array.isArray(value),
    array: Array.isArray(value),
    string: typeof value === 'string',
    boolean: typeof value === 'boolean',
    number: typeof value === 'number' && Number.isFinite(value),
    integer: typeof value === 'number' && Number.isSafeInteger(value)
  })[type] === true;
  const types = Array.isArray(schema.type) ? schema.type : schema.type ? [schema.type] : [];
  if (types.length && !types.some(match)) return [`${path}: expected ${types.join('|')}`];
  if (schema.enum && !schema.enum.some(x => Object.is(x, value))) errors.push(`${path}: value outside enum`);
  if (typeof value === 'number') {
    if (schema.minimum !== undefined && value < schema.minimum) errors.push(`${path}: below minimum`);
    if (schema.maximum !== undefined && value > schema.maximum) errors.push(`${path}: above maximum`);
    if (schema.exclusiveMinimum !== undefined && value <= schema.exclusiveMinimum) errors.push(`${path}: not above exclusive minimum`);
  }
  if (typeof value === 'string') {
    if (schema.minLength !== undefined && [...value].length < schema.minLength) errors.push(`${path}: string too short`);
    if (schema.maxLength !== undefined && [...value].length > schema.maxLength) errors.push(`${path}: string too long`);
  }
  if (Array.isArray(value)) {
    if (schema.minItems !== undefined && value.length < schema.minItems) errors.push(`${path}: array too short`);
    if (schema.maxItems !== undefined && value.length > schema.maxItems) errors.push(`${path}: array too long`);
    if (schema.items) value.forEach((item, i) => errors.push(...validate(schema.items, item, defs, `${path}[${i}]`)));
  } else if (value !== null && typeof value === 'object') {
    for (const field of schema.required ?? []) if (!Object.hasOwn(value, field)) errors.push(`${path}.${field}: required`);
    for (const [field, item] of Object.entries(value)) {
      const property = schema.properties?.[field];
      if (property) errors.push(...validate(property, item, defs, `${path}.${field}`));
      else if (schema.additionalProperties === false) errors.push(`${path}.${field}: unknown field`);
    }
  }
  return errors;
}

/** Report specific projection risks from the observed limited converter profile.
 * This does not execute or reproduce the converter, and is not a full schema diff.
 */
export function auditAdapterLoss(schema, path = '$') {
  const reports = [];
  const issue = (keyword, reason) => reports.push({path, keyword, reason});
  if (Array.isArray(schema.type)) issue('type', 'Type-array union has no matching scalar-type conversion branch.');
  if (schema.type === 'integer') issue('type', 'Integer declaration shares the number conversion branch.');
  if (schema.enum && schema.type !== 'string') issue('enum', 'Only the string conversion branch reads enum.');
  for (const key of ['minItems', 'maxItems', 'uniqueItems', 'minLength', 'maxLength', 'pattern', 'format', 'multipleOf', 'exclusiveMinimum', 'exclusiveMaximum']) {
    if (Object.hasOwn(schema, key)) issue(key, 'This keyword is not handled by the bounded converter profile.');
  }
  if (schema.additionalProperties === false) issue('additionalProperties', 'Nested object conversion uses passthrough.');
  for (const key of ['oneOf', 'anyOf', 'allOf']) if (schema[key]) issue(key, 'Object-shape detection is not validation of each combinator branch.');
  for (const [name, property] of Object.entries(schema.properties ?? {})) reports.push(...auditAdapterLoss(property, `${path}.${name}`));
  if (schema.items && !Array.isArray(schema.items)) reports.push(...auditAdapterLoss(schema.items, `${path}[]`));
  return reports;
}

export class ToolRouter {
  constructor(definitions, {readGrants}) {
    this.definitions = new Map(definitions.map(d => [d.name, d]));
    if (this.definitions.size !== definitions.length) throw new Error('duplicate tool name');
    this.readGrants = readGrants;
  }
  prepare(name, input) {
    const definition = this.definitions.get(name);
    if (!definition) throw new Error('unknown tool');
    const errors = validate(definition.schema, input, definition.defs);
    if (errors.length) throw new Error(errors.join('; '));
    const problem = definition.refine?.(input);
    if (problem) throw new Error(problem);
    return {definition, input: structuredClone(input)};
  }
  authorize(prepared) {
    const current = this.readGrants();
    if (!current.has(prepared.definition.capability)) throw new Error('capability denied');
  }
  async call(name, input) {
    const prepared = this.prepare(name, input);
    this.authorize(prepared);
    return prepared.definition.run(prepared.input);
  }
  async batch(actions) {
    // Deliberate teaching choice: preflight every shape before the first effect.
    if (!Array.isArray(actions) || !actions.length) throw new Error('non-empty action list required');
    const prepared = actions.map(a => this.prepare(a.name, a.input));
    const results = [];
    for (const item of prepared) {
      // Deliberate teaching choice: refresh grants for each action.
      this.authorize(item);
      results.push(await item.definition.run(item.input));
    }
    return results; // Earlier effects are not rolled back when a later action fails.
  }
}

export const exampleSchemas = {
  tap: {type: 'object', additionalProperties: false, required: ['point'], properties: {
    point: {type: 'array', minItems: 2, maxItems: 2, items: {type: 'integer', minimum: 0}},
    count: {type: 'integer', enum: [1, 2, 3]}
  }},
  menu: {type: 'object', required: ['selection'], properties: {
    selection: {type: ['string', 'array', 'null'], items: {type: 'string'}, maxItems: 4}
  }},
  clipboard: {type: 'object', required: ['text'], properties: {text: {type: 'string', maxLength: 256}}}
};
