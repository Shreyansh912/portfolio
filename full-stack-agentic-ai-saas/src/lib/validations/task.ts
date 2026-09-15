import { z } from 'zod';

export const createTaskSchema = z.object({
  title: z
    .string()
    .min(3, { message: 'Title must be at least 3 characters long' })
    .max(100, { message: 'Title cannot exceed 100 characters' }),
  prompt: z
    .string()
    .min(10, { message: 'Prompt must be at least 10 characters long' })
    .max(2000, { message: 'Prompt cannot exceed 2000 characters' }),
});

export type CreateTaskInput = z.infer<typeof createTaskSchema>;