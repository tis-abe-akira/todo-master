import type { Subtask } from "@/types/todo";
import { SubtaskItem } from "./SubtaskItem";

type SubtaskListProps = {
  subtasks: Subtask[];
};

export function SubtaskList({ subtasks }: SubtaskListProps) {
  if (subtasks.length === 0) {
    return null;
  }

  return (
    <div className="mt-4 pt-3 border-t border-[#E8E6E1]">
      <h4 className="text-xs font-semibold text-[#5C5A55] mb-2 px-2 uppercase tracking-wider">
        AI-Generated Subtasks
      </h4>
      <div className="overflow-hidden transition-all duration-500 ease-in-out">
        <ul className="space-y-1">
          {subtasks.map((subtask, index) => (
            <SubtaskItem key={index} index={index} title={subtask.title} />
          ))}
        </ul>
      </div>
    </div>
  );
}
