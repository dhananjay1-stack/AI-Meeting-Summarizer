import { useEffect, useState } from 'react';
import { settingsAPI } from '../lib/api';
import { Save, Check } from 'lucide-react';
import './SettingsPage.css';

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    default_ai_provider: 'ollama',
    default_whisper_model: 'base',
    enable_diarization: false,
    default_export_format: 'pdf',
    theme: 'dark',
  });
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const res = await settingsAPI.get();
      setSettings(res.data);
    } catch (err) {
      console.error('Failed to load settings:', err);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setSaved(false);
    try {
      await settingsAPI.update(settings);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      console.error('Failed to save settings:', err);
    } finally {
      setSaving(false);
    }
  };

  const updateSetting = (key: string, value: any) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <div className="settings-page">
      <div className="page-container" style={{ maxWidth: 720 }}>
        <div className="page-header animate-fade-in">
          <h1 className="page-title">
            <span className="gradient-text">Settings</span>
          </h1>
          <p className="page-subtitle">Configure your preferences</p>
        </div>

        <div className="settings-card glass-card animate-slide-up">
          {/* AI Provider */}
          <div className="settings-group">
            <h3>AI Configuration</h3>

            <div className="settings-field">
              <label>Summarization Provider</label>
              <select
                className="input-field"
                value={settings.default_ai_provider}
                onChange={(e) => updateSetting('default_ai_provider', e.target.value)}
              >
                <option value="ollama">Ollama (Local)</option>
                <option value="openai">OpenAI</option>
                <option value="claude">Claude</option>
                <option value="gemini">Gemini</option>
              </select>
            </div>

            <div className="settings-field">
              <label>Whisper Model Size</label>
              <select
                className="input-field"
                value={settings.default_whisper_model}
                onChange={(e) => updateSetting('default_whisper_model', e.target.value)}
              >
                <option value="tiny">Tiny (fastest)</option>
                <option value="base">Base (recommended)</option>
                <option value="small">Small</option>
                <option value="medium">Medium</option>
                <option value="large-v3">Large V3 (most accurate)</option>
              </select>
            </div>

            <div className="settings-field">
              <label className="settings-toggle-label">
                <span>Speaker Diarization</span>
                <div
                  className={`settings-toggle ${settings.enable_diarization ? 'active' : ''}`}
                  onClick={() => updateSetting('enable_diarization', !settings.enable_diarization)}
                >
                  <div className="settings-toggle-thumb" />
                </div>
              </label>
              <p className="settings-hint">Identify different speakers (requires HuggingFace token)</p>
            </div>
          </div>

          {/* Export */}
          <div className="settings-group">
            <h3>Export Preferences</h3>

            <div className="settings-field">
              <label>Default Export Format</label>
              <select
                className="input-field"
                value={settings.default_export_format}
                onChange={(e) => updateSetting('default_export_format', e.target.value)}
              >
                <option value="pdf">PDF</option>
                <option value="docx">DOCX (Word)</option>
                <option value="txt">Plain Text</option>
              </select>
            </div>
          </div>

          {/* Save */}
          <button className="btn-primary settings-save" onClick={handleSave} disabled={saving}>
            {saved ? (
              <><Check size={18} /> Saved!</>
            ) : saving ? (
              <><span className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} /> Saving...</>
            ) : (
              <><Save size={18} /> Save Settings</>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
