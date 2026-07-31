"use client";

import { FileText, Upload, CheckCircle2, Trash2 } from "lucide-react";
import { useResumes } from "@/lib/hooks";
import { apiClient } from "@/lib/api-client";
import { formatDate, cn } from "@/lib/utils";
import { useCallback, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";

export default function ResumesPage() {
  const { data: resumes = [], isLoading } = useResumes();
  const qc = useQueryClient();
  const [uploading, setUploading] = useState(false);

  const handleUpload = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;
      if (file.type !== "application/pdf") {
        toast.error("Only PDF files are accepted");
        return;
      }

      setUploading(true);
      const formData = new FormData();
      formData.append("file", file);

      try {
        await apiClient.post("/resumes/upload", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        toast.success("Resume uploaded!");
        qc.invalidateQueries({ queryKey: ["resumes"] });
      } catch {
        toast.error("Upload failed");
      } finally {
        setUploading(false);
        e.target.value = "";
      }
    },
    [qc]
  );

  const handleActivate = async (id: string) => {
    try {
      await apiClient.post(`/resumes/${id}/activate`);
      toast.success("Resume activated");
      qc.invalidateQueries({ queryKey: ["resumes"] });
    } catch {
      toast.error("Failed to activate");
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await apiClient.delete(`/resumes/${id}`);
      toast.success("Resume deleted");
      qc.invalidateQueries({ queryKey: ["resumes"] });
    } catch {
      toast.error("Failed to delete");
    }
  };

  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Resumes</h1>
          <p className="mt-1 text-sm text-surface-200/70">
            Upload and manage your resume versions
          </p>
        </div>
        <label className="btn-primary cursor-pointer">
          <Upload size={16} />
          {uploading ? "Uploading..." : "Upload PDF"}
          <input
            type="file"
            accept=".pdf"
            className="hidden"
            onChange={handleUpload}
            disabled={uploading}
          />
        </label>
      </div>

      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2">
          {[...Array(2)].map((_, i) => (
            <div key={i} className="skeleton h-40 rounded-xl" />
          ))}
        </div>
      ) : resumes.length === 0 ? (
        <div className="card flex flex-col items-center justify-center py-20 text-center">
          <FileText size={48} className="text-surface-200/20" />
          <p className="mt-4 text-surface-200/60">
            No resumes uploaded. Upload a PDF to get started with AI matching.
          </p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {resumes.map((resume) => (
            <div
              key={resume.id}
              className={cn(
                "card-hover relative p-5",
                resume.is_active && "ring-1 ring-brand-500/50"
              )}
            >
              {resume.is_active && (
                <div className="absolute -top-2 right-4">
                  <span className="badge-success flex items-center gap-1 text-[10px]">
                    <CheckCircle2 size={10} /> Active
                  </span>
                </div>
              )}

              <div className="flex items-start gap-4">
                <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-brand-500/10">
                  <FileText size={22} className="text-brand-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-surface-50 truncate">
                    {resume.filename}
                  </h3>
                  <p className="mt-1 text-xs text-surface-200/50">
                    Uploaded {formatDate(resume.created_at)}
                  </p>
                  {resume.extracted_text && (
                    <p className="mt-2 text-xs text-surface-200/40 line-clamp-3">
                      {resume.extracted_text.substring(0, 200)}...
                    </p>
                  )}
                </div>
              </div>

              <div className="mt-4 flex items-center gap-2">
                {!resume.is_active && (
                  <button
                    onClick={() => handleActivate(resume.id)}
                    className="btn-primary btn-sm"
                  >
                    <CheckCircle2 size={14} />
                    Set Active
                  </button>
                )}
                <button
                  onClick={() => handleDelete(resume.id)}
                  className="btn-danger btn-sm"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
