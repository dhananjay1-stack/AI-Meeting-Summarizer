import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../lib/auth';
import { meetingAPI } from '../lib/api';
import {
  Plus, Search, Mic, CheckCircle, Clock,
  Trash2, ChevronRight, BarChart3, Timer, Sparkles
} from 'lucide-react';
import './DashboardPage.css';

interface Meeting {
  id: string;
  title: string;
  description: string | null;
  status: string;
  duration_seconds: number | null;
  created_at: string;
  has_transcript: boolean;
  has_summary: boolean;
  action_item_count: number;
}

interface Stats {
  total_meetings: number;
  completed_meetings: number;
  total_duration_seconds: number;
}

export default function DashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    loadData();
  }, [page]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [meetingsRes, statsRes] = await Promise.all([
        meetingAPI.list(page, 12),
        meetingAPI.getStats(),
      ]);
      setMeetings(meetingsRes.data.meetings);
      setTotalPages(meetingsRes.data.total_pages);
      setStats(statsRes.data);
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      loadData();
      return;
    }
    setLoading(true);
    try {
      const res = await meetingAPI.search(searchQuery);
      setMeetings(res.data.meetings);
      setTotalPages(res.data.total_pages);
    } catch (err) {
      console.error('Search failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Delete this meeting? This cannot be undone.')) return;
    try {
      await meetingAPI.delete(id);
      setMeetings((prev) => prev.filter((m) => m.id !== id));
    } catch (err) {
      console.error('Delete failed:', err);
    }
  };

  const getStatusBadge = (status: string) => {
    const map: Record<string, { class: string; label: string }> = {
      uploaded: { class: 'badge-info', label: 'Uploaded' },
      transcribing: { class: 'badge-processing', label: 'Transcribing' },
      summarizing: { class: 'badge-processing', label: 'Summarizing' },
      cleaning: { class: 'badge-processing', label: 'Processing' },
      extracting: { class: 'badge-processing', label: 'Extracting' },
      completed: { class: 'badge-success', label: 'Completed' },
      failed: { class: 'badge-error', label: 'Failed' },
    };
    const s = map[status] || { class: 'badge-info', label: status };
    return <span className={`badge ${s.class}`}>{s.label}</span>;
  };

  const formatDuration = (seconds: number | null) => {
    if (!seconds) return '—';
    const m = Math.floor(seconds / 60);
    return `${m} min`;
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <div className="dashboard-page">
      <div className="page-container">
        {/* Header */}
        <div className="dashboard-header animate-fade-in">
          <div>
            <h1 className="page-title">
              Welcome back, <span className="gradient-text">{user?.username}</span>
            </h1>
            <p className="page-subtitle">Here's an overview of your meetings</p>
          </div>
          <Link to="/upload" className="btn-primary">
            <Plus size={18} /> New Meeting
          </Link>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="stats-grid animate-slide-up">
            <div className="stat-card glass-card">
              <div className="stat-icon" style={{ background: 'rgba(139, 92, 246, 0.15)' }}>
                <BarChart3 size={22} color="var(--accent-purple)" />
              </div>
              <div className="stat-info">
                <span className="stat-value">{stats.total_meetings}</span>
                <span className="stat-label">Total Meetings</span>
              </div>
            </div>
            <div className="stat-card glass-card">
              <div className="stat-icon" style={{ background: 'rgba(34, 197, 94, 0.15)' }}>
                <CheckCircle size={22} color="var(--success)" />
              </div>
              <div className="stat-info">
                <span className="stat-value">{stats.completed_meetings}</span>
                <span className="stat-label">Completed</span>
              </div>
            </div>
            <div className="stat-card glass-card">
              <div className="stat-icon" style={{ background: 'rgba(59, 130, 246, 0.15)' }}>
                <Timer size={22} color="var(--accent-blue)" />
              </div>
              <div className="stat-info">
                <span className="stat-value">
                  {Math.round((stats.total_duration_seconds || 0) / 60)}
                </span>
                <span className="stat-label">Minutes Processed</span>
              </div>
            </div>
          </div>
        )}

        {/* Search Bar */}
        <div className="search-section animate-slide-up" style={{ animationDelay: '0.1s' }}>
          <div className="search-bar glass-card">
            <Search size={18} className="search-icon" />
            <input
              type="text"
              className="search-input"
              placeholder="Search meetings by title, description, or transcript..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
            <button className="btn-primary search-btn" onClick={handleSearch}>
              Search
            </button>
          </div>
        </div>

        {/* Meetings Grid */}
        {loading ? (
          <div className="loading-center">
            <div className="spinner spinner-lg" />
            <p>Loading meetings...</p>
          </div>
        ) : meetings.length === 0 ? (
          <div className="empty-state animate-fade-in">
            <Sparkles size={48} />
            <h3>No meetings yet</h3>
            <p>Upload your first meeting audio to get started</p>
            <Link to="/upload" className="btn-primary">
              <Plus size={18} /> Upload Meeting
            </Link>
          </div>
        ) : (
          <>
            <div className="meetings-grid">
              {meetings.map((meeting, idx) => (
                <div
                  key={meeting.id}
                  className="meeting-card glass-card animate-slide-up"
                  style={{ animationDelay: `${0.05 * idx}s` }}
                  onClick={() => navigate(`/meetings/${meeting.id}`)}
                >
                  <div className="meeting-card-header">
                    <h3 className="meeting-card-title">{meeting.title}</h3>
                    <button
                      className="btn-ghost meeting-delete"
                      onClick={(e) => handleDelete(meeting.id, e)}
                      title="Delete meeting"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                  {meeting.description && (
                    <p className="meeting-card-desc">{meeting.description}</p>
                  )}
                  <div className="meeting-card-meta">
                    <span className="meeting-card-date">
                      <Clock size={14} /> {formatDate(meeting.created_at)}
                    </span>
                    {meeting.duration_seconds && (
                      <span className="meeting-card-duration">
                        <Timer size={14} /> {formatDuration(meeting.duration_seconds)}
                      </span>
                    )}
                  </div>
                  <div className="meeting-card-footer">
                    <div className="meeting-card-badges">
                      {getStatusBadge(meeting.status)}
                      {meeting.has_transcript && (
                        <span className="badge badge-info"><Mic size={10} /> Transcript</span>
                      )}
                      {meeting.action_item_count > 0 && (
                        <span className="badge badge-warning">
                          {meeting.action_item_count} action{meeting.action_item_count !== 1 && 's'}
                        </span>
                      )}
                    </div>
                    <ChevronRight size={18} className="meeting-card-arrow" />
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="pagination">
                <button
                  className="btn-secondary"
                  disabled={page === 1}
                  onClick={() => setPage(page - 1)}
                >
                  Previous
                </button>
                <span className="pagination-info">
                  Page {page} of {totalPages}
                </span>
                <button
                  className="btn-secondary"
                  disabled={page === totalPages}
                  onClick={() => setPage(page + 1)}
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
