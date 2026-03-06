export type Todo = {
  id: string;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
};

export type CreateTodoRequest = {
  title: string;
  description?: string;
};

export type UpdateTodoRequest = {
  title?: string;
  description?: string;
  completed?: boolean;
};

export type Subtask = {
  title: string;
};

export type SubtasksResponse = {
  subtasks: Subtask[];
};
