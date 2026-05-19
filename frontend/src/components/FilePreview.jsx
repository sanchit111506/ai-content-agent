import {
  FileText,
  FileImage,
  FileSpreadsheet,
  FileCode,
  File as FileIcon,
  X,
} from "lucide-react";

/**
 * FilePreview — used in two places:
 *   1. Above the input (with removable=true, onRemove callback)
 *   2. Inside a user message (read-only)
 */
function getFileIcon(filename) {
  const ext = filename.split(".").pop()?.toLowerCase();
  if (["pdf", "doc", "docx", "txt"].includes(ext))
    return { Icon: FileText, color: "text-red-400" };
  if (["xls", "xlsx", "csv"].includes(ext))
    return { Icon: FileSpreadsheet, color: "text-green-400" };
  if (["png", "jpg", "jpeg", "gif", "webp", "svg"].includes(ext))
    return { Icon: FileImage, color: "text-blue-400" };
  if (["js", "jsx", "ts", "tsx", "py", "json", "html", "css"].includes(ext))
    return { Icon: FileCode, color: "text-yellow-400" };
  return { Icon: FileIcon, color: "text-zinc-400" };
}

function formatSize(bytes) {
  if (!bytes) return "";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function FilePreview({ files, removable = false, onRemove }) {
  if (!files || files.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2 mb-2">
      {files.map((file, index) => {
        const { Icon, color } = getFileIcon(file.name);
        return (
          <div
            key={index}
            className="group flex items-center gap-2 bg-[#1f1f1f] border border-zinc-800 px-3 py-2 rounded-lg text-sm max-w-[220px]"
          >
            <Icon size={16} className={`${color} flex-shrink-0`} />
            <div className="flex flex-col min-w-0 flex-1">
              <span className="truncate text-zinc-200 text-xs font-medium">
                {file.name}
              </span>
              {file.size && (
                <span className="text-zinc-500 text-[10px]">
                  {formatSize(file.size)}
                </span>
              )}
            </div>
            {removable && (
              <button
                onClick={() => onRemove?.(index)}
                className="p-0.5 rounded hover:bg-zinc-700 text-zinc-500 hover:text-red-400 transition flex-shrink-0"
                title="Remove"
              >
                <X size={14} />
              </button>
            )}
          </div>
        );
      })}
    </div>
  );
}
