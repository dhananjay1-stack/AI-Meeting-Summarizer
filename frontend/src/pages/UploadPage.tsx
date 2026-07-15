import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { meetingAPI } from '../lib/api';
import { Upload, FileAudio, X, Check, AlertCircle } from 'lucide-react';
import './UploadPage.css';

export default function UploadPage() {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');
  const [step, setStep] = useState<'details' | 'upload' | 'processing'>('details');

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) setFile(droppedFile);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) setFile(selected);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes >= 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    return `${(bytes / 1024).toFixed(1)} KB`;
  };

  const handleSubmit = async () => {
    if (!title.trim()) { setError('Please enter a meeting title.'); return; }
    if (!file) { setError('Please select an audio file.'); return; }
    setError('');
    setUploading(true);
    setStep('upload');

    try {
      // Step 1: Create meeting
      const createRes = await meetingAPI.create({ title, description: description || undefined });
      const meetingId = createRes.data.id;

      // Step 2: Upload file
      await meetingAPI.upload(meetingId, file, (pct) => setProgress(pct));

      setStep('processing');

      // Redirect to meeting detail after a brief delay
      setTimeout(() => navigate(`/meetings/${meetingId}`), 1500);
    } catch (err: any) {
      setError(err.response?.data?.message || err.response?.data?.detail || 'Upload failed.');
      setStep('details');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="upload-page">
      <div className="page-container" style={{ maxWidth: 720 }}>
        <div className="page-header animate-fade-in">
          <h1 className="page-title">
            <span className="gradient-text">Upload Meeting</span>
          </h1>
          <p className="page-subtitle">Upload an audio file to transcribe and summarize</p>
        </div>

        <div className="upload-card glass-card animate-slide-up">
          {step === 'processing' ? (
            <div className="upload-success">
              <div className="upload-success-icon">
                <Check size={32} />
              </div>
              <h3>Upload Complete!</h3>
              <p>Your meeting is being processed. Redirecting...</p>
              <div className="spinner" />
            </div>
          ) : (
            <>
              {error && (
                <div className="upload-error">
                  <AlertCircle size={16} /> {error}
                </div>
              )}

              {/* Title Input */}
              <div className="upload-field">
                <label>Meeting Title *</label>
                <input
                  type="text"
                  className="input-field"
                  placeholder="e.g., Weekly Team Standup"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  disabled={uploading}
                />
              </div>

              {/* Description */}
              <div className="upload-field">
                <label>Description (optional)</label>
                <textarea
                  className="input-field upload-textarea"
                  placeholder="Brief description of the meeting..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  disabled={uploading}
                  rows={3}
                />
              </div>

              {/* File Drop Zone */}
              <div className="upload-field">
                <label>Audio File *</label>
                <div
                  className={`upload-dropzone ${dragOver ? 'upload-dropzone-active' : ''} ${file ? 'upload-dropzone-has-file' : ''}`}
                  onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                  onDragLeave={() => setDragOver(false)}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".mp3,.wav,.m4a,.ogg,.flac,.webm,.mp4,.wma"
                    onChange={handleFileSelect}
                    hidden
                  />

                  {file ? (
                    <div className="upload-file-info">
                      <FileAudio size={28} color="var(--accent-purple)" />
                      <div>
                        <p className="upload-file-name">{file.name}</p>
                        <p className="upload-file-size">{formatFileSize(file.size)}</p>
                      </div>
                      <button
                        className="btn-ghost"
                        onClick={(e) => { e.stopPropagation(); setFile(null); }}
                      >
                        <X size={18} />
                      </button>
                    </div>
                  ) : (
                    <div className="upload-dropzone-content">
                      <Upload size={36} />
                      <p>Drag & drop your audio file here</p>
                      <span>or click to browse</span>
                      <span className="upload-formats">
                        MP3, WAV, M4A, OGG, FLAC, WEBM, MP4 • Max 500MB
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* Progress Bar */}
              {uploading && (
                <div className="upload-progress animate-fade-in">
                  <div className="upload-progress-bar">
                    <div
                      className="upload-progress-fill"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                  <span className="upload-progress-text">{progress}% uploaded</span>
                </div>
              )}

              {/* Submit */}
              <button
                className="btn-primary upload-submit"
                onClick={handleSubmit}
                disabled={uploading || !title.trim() || !file}
              >
                {uploading ? (
                  <><span className="spinner" style={{ width: 20, height: 20, borderWidth: 2 }} /> Uploading...</>
                ) : (
                  <><Upload size={18} /> Upload & Process</>
                )}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
