import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { meetingAPI } from '../lib/api';
import {
  ArrowLeft, Download, Clock, Timer, Globe, Mic, FileText,
  CheckSquare, Tag, Copy, Check
} from 'lucide-react';
import './MeetingDetailPage.css';

export default function MeetingDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'summary' | 'transcript' | 'actions'>('summary');
  const [exporting, setExporting] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    loadMeeting();
  }, [id]);

  // Auto-refresh while processing
  useEffect(() => {
    if (!data) return;
    const processingStatuses = ['uploaded', 'transcribing', 'cleaning', 'summarizing', 'extracting'];
    if (processingStatuses.includes(data.meeting.status)) {
      const timer = setInterval(loadMeeting, 5000);
      return () => clearInterval(timer);
    }
  }, [data?.meeting?.status]);

  const loadMeeting = async () => {
    try {
      const res = await meetingAPI.get(id!);
      setData(res.data);
    } catch {
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format: string) => {
    setExporting(true);
    try {
      const res = await meetingAPI.export(id!, format);
      const blob = new Blob([res.data]);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${data.meeting.title}_summary.${format}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Export failed:', err);
    } finally {
      setExporting(false);
    }
  };

  const handleCopy = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback
      const textarea = document.createElement('textarea');
      textarea.value = text;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleActionItemToggle = async (itemId: string, currentStatus: string) => {
    const newStatus = currentStatus === 'completed' ? 'pending' : 'completed';
    try {
      await meetingAPI.updateActionItem(id!, itemId, { status: newStatus });
      loadMeeting();
    } catch (err) {
      console.error('Failed to update action item:', err);
    }
  };

  const formatDuration = (s: number | null) => s ? `${Math.floor(s / 60)} min` : '—';

  if (loading) {
    return (
      <div className="meeting-detail-page">
        <div className="loading-center"><div className="spinner spinner-lg" /><p>Loading...</p></div>
      </div>
    );
  }

  if (!data) return null;

  const { meeting, transcript, summary, action_items, keywords } = data;
  const isProcessing = !['completed', 'failed'].includes(meeting.status);

  return (
    <div className="meeting-detail-page">
      <div className="page-container">
        {/* Back Button */}
        <button className="btn-ghost detail-back" onClick={() => navigate('/')}>
          <ArrowLeft size={18} /> Back to Dashboard
        </button>

        {/* Header */}
        <div className="detail-header animate-fade-in">
          <div className="detail-header-info">
            <h1 className="page-title">{meeting.title}</h1>
            {meeting.description && <p className="page-subtitle">{meeting.description}</p>}
            <div className="detail-meta">
              <span><Clock size={14} /> {new Date(meeting.created_at).toLocaleDateString()}</span>
              {meeting.duration_seconds && <span><Timer size={14} /> {formatDuration(meeting.duration_seconds)}</span>}
              {transcript?.language && <span><Globe size={14} /> {transcript.language.toUpperCase()}</span>}
              {transcript?.confidence && <span>Confidence: {(transcript.confidence * 100).toFixed(1)}%</span>}
            </div>
          </div>

          {/* Status / Export */}
          <div className="detail-header-actions">
            {isProcessing ? (
              <div className="detail-processing">
                <div className="spinner" />
                <span className="badge badge-processing">
                  {meeting.status === 'transcribing' ? 'Transcribing...' :
                   meeting.status === 'summarizing' ? 'Summarizing...' :
                   meeting.status === 'extracting' ? 'Extracting...' :
                   'Processing...'}
                </span>
              </div>
            ) : meeting.status === 'failed' ? (
              <div className="detail-failed">
                <span className="badge badge-error">Failed</span>
                <p className="detail-error-msg">{meeting.error_message}</p>
              </div>
            ) : (
              <div className="export-buttons">
                <button className="btn-secondary" onClick={() => handleExport('pdf')} disabled={exporting}>
                  <Download size={16} /> PDF
                </button>
                <button className="btn-secondary" onClick={() => handleExport('docx')} disabled={exporting}>
                  <Download size={16} /> DOCX
                </button>
                <button className="btn-secondary" onClick={() => handleExport('txt')} disabled={exporting}>
                  <Download size={16} /> TXT
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Keywords */}
        {keywords && keywords.length > 0 && (
          <div className="detail-keywords animate-fade-in">
            <Tag size={14} />
            {keywords.map((kw: any, i: number) => (
              <span key={i} className="keyword-tag">{kw.keyword}</span>
            ))}
          </div>
        )}

        {/* Tabs */}
        {meeting.status === 'completed' && (
          <>
            <div className="detail-tabs animate-fade-in">
              <button
                className={`detail-tab ${activeTab === 'summary' ? 'active' : ''}`}
                onClick={() => setActiveTab('summary')}
              >
                <FileText size={16} /> Summary
              </button>
              <button
                className={`detail-tab ${activeTab === 'transcript' ? 'active' : ''}`}
                onClick={() => setActiveTab('transcript')}
              >
                <Mic size={16} /> Transcript
              </button>
              <button
                className={`detail-tab ${activeTab === 'actions' ? 'active' : ''}`}
                onClick={() => setActiveTab('actions')}
              >
                <CheckSquare size={16} /> Actions ({action_items?.length || 0})
              </button>
            </div>

            {/* Tab Content */}
            <div className="detail-content glass-card animate-slide-up">
              {activeTab === 'summary' && (
                <div className="summary-content">
                  {summary ? (
                    <>
                      {/* Copy button */}
                      <button
                        className="btn-ghost detail-copy-btn"
                        onClick={() => handleCopy(summary.executive_summary)}
                        title="Copy to clipboard"
                      >
                        {copied ? <Check size={16} /> : <Copy size={16} />}
                        {copied ? 'Copied!' : 'Copy'}
                      </button>

                      <div className="summary-section">
                        <h3>Executive Summary</h3>
                        <p>{summary.executive_summary}</p>
                      </div>

                      {summary.key_points?.length > 0 && (
                        <div className="summary-section">
                          <h3>Key Points</h3>
                          <ul className="summary-list">
                            {summary.key_points.map((point: string, i: number) => (
                              <li key={i}>{point}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {summary.decisions?.length > 0 && (
                        <div className="summary-section">
                          <h3>Decisions Made</h3>
                          <ul className="summary-list decisions">
                            {summary.decisions.map((d: string, i: number) => (
                              <li key={i}>{d}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      <div className="summary-meta">
                        <span>AI: {summary.ai_provider} / {summary.ai_model}</span>
                        {summary.processing_time && <span>Processed in {summary.processing_time}s</span>}
                      </div>
                    </>
                  ) : (
                    <div className="empty-state">
                      <FileText size={36} />
                      <p>No summary available for this meeting.</p>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'transcript' && (
                <div className="transcript-content">
                  {transcript ? (
                    <>
                      <button
                        className="btn-ghost detail-copy-btn"
                        onClick={() => handleCopy(transcript.full_text)}
                        title="Copy to clipboard"
                      >
                        {copied ? <Check size={16} /> : <Copy size={16} />}
                        {copied ? 'Copied!' : 'Copy'}
                      </button>

                      {transcript.segments?.length > 0 ? (
                        <div className="transcript-segments">
                          {transcript.segments.map((seg: any, i: number) => (
                            <div key={i} className="transcript-segment">
                              <span className="segment-time">
                                {Math.floor(seg.start / 60)}:{String(Math.floor(seg.start % 60)).padStart(2, '0')}
                              </span>
                              <p className="segment-text">{seg.text}</p>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="transcript-full-text">{transcript.full_text}</p>
                      )}
                    </>
                  ) : (
                    <div className="empty-state">
                      <Mic size={36} />
                      <p>No transcript available for this meeting.</p>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'actions' && (
                <div className="actions-content">
                  {action_items?.length > 0 ? (
                    <div className="action-items-list">
                      {action_items.map((item: any) => (
                        <div
                          key={item.id}
                          className={`action-item ${item.status === 'completed' ? 'action-item-done' : ''}`}
                        >
                          <button
                            className="action-item-check"
                            onClick={() => handleActionItemToggle(item.id, item.status)}
                          >
                            {item.status === 'completed' ? (
                              <CheckSquare size={20} color="var(--success)" />
                            ) : (
                              <div className="action-item-checkbox" />
                            )}
                          </button>
                          <div className="action-item-info">
                            <p className="action-item-desc">{item.description}</p>
                            <div className="action-item-meta">
                              {item.assignee && <span>👤 {item.assignee}</span>}
                              <span className={`badge badge-${item.priority === 'high' ? 'error' : item.priority === 'medium' ? 'warning' : 'info'}`}>
                                {item.priority}
                              </span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="empty-state">
                      <CheckSquare size={36} />
                      <p>No action items identified</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
