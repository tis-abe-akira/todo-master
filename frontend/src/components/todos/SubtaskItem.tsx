type SubtaskItemProps = {
  index: number;
  title: string;
};

export function SubtaskItem({ index, title }: SubtaskItemProps) {
  return (
    <li className="flex items-start gap-2 py-1.5 px-2 hover:bg-[#F7F5F2] rounded-md transition-colors">
      <span className="text-xs font-mono font-medium text-[#5C5A55] min-w-[20px] text-right mt-[2px]">
        {index + 1}.
      </span>
      <span className="text-sm text-[#3D3A31] leading-relaxed flex-1">
        {title}
      </span>
    </li>
  );
}
