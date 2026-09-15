export interface AgentToolDefinition {
  type: 'function';
  function: {
    name: string;
    description: string;
    parameters: Record<string, any>;
  };
}

export const availableTools: AgentToolDefinition[] = [
  {
    type: 'function',
    function: {
      name: 'calculate',
      description: 'Safely evaluates basic arithmetic expressions (addition, subtraction, multiplication, division, ratios).',
      parameters: {
        type: 'object',
        properties: {
          expression: {
            type: 'string',
            description: 'The math expression to evaluate, e.g., "59990 / 16" or "250 * 1.18"',
          },
        },
        required: ['expression'],
      },
    },
  },
  {
    type: 'function',
    function: {
      name: 'getCurrentDateTime',
      description: 'Returns the current server UTC timestamp and formatted date string.',
      parameters: {
        type: 'object',
        properties: {},
      },
    },
  },
];

export async function executeTool(name: string, args: Record<string, any>): Promise<string> {
  switch (name) {
    case 'calculate': {
      const sanitized = String(args.expression).replace(/[^0-9+\-*/().\s]/g, '');
      try {
        // Evaluate safe arithmetic expression
        const result = Function(`'use strict'; return (${sanitized})`)();
        return JSON.stringify({ expression: args.expression, result: Number(result.toFixed(4)) });
      } catch (err) {
        return JSON.stringify({ error: 'Failed to evaluate expression safely.' });
      }
    }
    case 'getCurrentDateTime': {
      const now = new Date();
      return JSON.stringify({
        iso: now.toISOString(),
        utcFormatted: now.toUTCString(),
      });
    }
    default:
      return JSON.stringify({ error: `Tool "${name}" is not implemented.` });
  }
}