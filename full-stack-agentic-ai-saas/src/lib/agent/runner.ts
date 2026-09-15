import OpenAI from 'openai';
import { availableTools, executeTool } from './tools';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export interface RunAgentParams {
  prompt: string;
  systemPrompt?: string;
  maxIterations?: number;
}

export interface RunStepLog {
  role: 'assistant' | 'tool' | 'user';
  content?: string | null;
  tool_calls?: any[];
  tool_name?: string;
  tool_result?: string;
}

export async function runAgentExecutionLoop({
  prompt,
  systemPrompt = 'You are an autonomous AI task execution agent for AgentFlow AI. Use provided tools whenever calculations, timestamps, or verified logic are required. Provide clear, structured reports upon completion.',
  maxIterations = 5,
}: RunAgentParams) {
  const messages: OpenAI.Chat.Completions.ChatCompletionMessageParam[] = [
    { role: 'system', content: systemPrompt },
    { role: 'user', content: prompt },
  ];

  const logs: RunStepLog[] = [];
  let currentIteration = 0;
  let finalResponse = '';

  while (currentIteration < maxIterations) {
    currentIteration++;

    const response = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages,
      tools: availableTools,
      tool_choice: 'auto',
    });

    const choice = response.choices[0];
    const assistantMessage = choice.message;
    messages.push(assistantMessage);

    if (assistantMessage.content) {
      finalResponse = assistantMessage.content;
    }

    // Check if the agent called any tools
    if (assistantMessage.tool_calls && assistantMessage.tool_calls.length > 0) {
      logs.push({
        role: 'assistant',
        content: assistantMessage.content,
        tool_calls: assistantMessage.tool_calls,
      });

      for (const toolCall of assistantMessage.tool_calls) {
        if (toolCall.type === 'function') {
          const functionName = toolCall.function.name;
          const parsedArgs = JSON.parse(toolCall.function.arguments || '{}');
          const toolOutput = await executeTool(functionName, parsedArgs);

          logs.push({
            role: 'tool',
            tool_name: functionName,
            tool_result: toolOutput,
          });

          messages.push({
            role: 'tool',
            tool_call_id: toolCall.id,
            content: toolOutput,
          });
        }
      }
    } else {
      // Agent finished its reasoning without further tool calls
      break;
    }
  }

  return {
    finalResponse,
    logs,
    iterations: currentIteration,
  };
}