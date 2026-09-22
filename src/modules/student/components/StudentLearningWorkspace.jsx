import React, { useState, useEffect } from 'react';
import { 
  BookOpen, 
  GraduationCap, 
  Calendar, 
  Users, 
  CheckCircle2, 
  AlertCircle, 
  Award, 
  Sparkles,
  UserCheck
} from 'lucide-react';
import api from '../../../lib/api';
import Button from '../../../components/Button';
import Loading from '../../../components/Loading';

const formatDate = (dateStr) => {
  if (!dateStr) return null;
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return String(dateStr);
    return d.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return String(dateStr);
  }
};

export default function StudentLearningWorkspace() {
  const [learningData, setLearningData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [enrollingId, setEnrollingId] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [successToast, setSuccessToast] = useState(null);

  const fetchLearningData = async () => {
    try {
      setLoading(true);
      setErrorMsg(null);
      const res = await api.get('/student/learning');
      setLearningData(res.data);
    } catch (err) {
      console.error('Failed to load learning workspace:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to load training programs data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLearningData();
  }, []);

  const handleEnroll = async (programId, programTitle) => {
    try {
      setEnrollingId(programId);
      setErrorMsg(null);
      await api.post(`/student/learning/enroll/${programId}`);
      setSuccessToast(`Successfully enrolled in "${programTitle}"!`);
      setTimeout(() => setSuccessToast(null), 4000);
      await fetchLearningData();
    } catch (err) {
      console.error('Failed to enroll:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to enroll in program.');
    } finally {
      setEnrollingId(null);
    }
  };

  if (loading) {
    return <Loading label="Loading training programs & enrollments..." />;
  }

  const rawAvailablePrograms = learningData?.available_programs || [];
  const availablePrograms = rawAvailablePrograms.filter((prog) => !prog.is_enrolled);
  const currentEnrollments = learningData?.current_enrollments || [];
  const enrolledCount = learningData?.enrolled_count || 0;
  const completedCount = learningData?.completed_count || 0;

  return (
    <div className="space-y-6">
      {/* Notifications */}
      {successToast && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-800 text-sm flex items-center justify-between shadow-sm animate-fade-in">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
            <span className="font-medium">{successToast}</span>
          </div>
        </div>
      )}

      {errorMsg && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-sm flex items-center justify-between shadow-sm">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0" />
            <span className="font-medium">{errorMsg}</span>
          </div>
          <button onClick={() => setErrorMsg(null)} className="text-rose-500 hover:text-rose-700 font-bold">
            ×
          </button>
        </div>
      )}

      {/* Header Banner */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 bg-blue-50 text-blue-600 rounded-xl">
              <BookOpen className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900">Training Programs & Workshops</h1>
              <p className="text-sm text-slate-500">
                Accredited college workshops, corporate bootcamps, and live skill masterclasses.
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <div className="px-4 py-2 bg-slate-50 border border-slate-100 rounded-xl text-center">
              <span className="block text-xs font-semibold text-slate-400 uppercase">Enrolled Programs</span>
              <span className="text-lg font-bold text-slate-900">{enrolledCount}</span>
            </div>
            <div className="px-4 py-2 bg-slate-50 border border-slate-100 rounded-xl text-center">
              <span className="block text-xs font-semibold text-slate-400 uppercase">Completed</span>
              <span className="text-lg font-bold text-emerald-600">{completedCount}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Section 1: My Current Enrollments */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
        <h2 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
          <GraduationCap className="w-5 h-5 text-blue-600" />
          <span>My Training Enrollments ({currentEnrollments.length})</span>
        </h2>

        {currentEnrollments.length === 0 ? (
          <div className="text-center py-8 bg-slate-50 rounded-xl border border-dashed border-slate-200">
            <BookOpen className="w-10 h-10 text-slate-300 mx-auto mb-2" />
            <p className="text-slate-600 font-medium text-sm">No Active Enrollments</p>
            <p className="text-slate-400 text-xs mt-1">Browse available programs below to enroll in your first bootcamp.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {currentEnrollments.map((enr) => {
              const prog = enr.training_program || {};
              const isComp = enr.completion_status === 'COMPLETED';

              return (
                <div
                  key={enr.id}
                  className={`border rounded-xl p-5 space-y-3 transition-all ${
                    isComp ? 'border-emerald-200 bg-emerald-50/20' : 'border-slate-200 bg-white'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-100">
                        {prog.program_type || 'BOOTCAMP'}
                      </span>
                      <h3 className="font-bold text-slate-900 text-base mt-2">{prog.title || 'Training Program'}</h3>
                    </div>

                    <span
                      className={`px-3 py-1 rounded-full text-xs font-bold ${
                        isComp
                          ? 'bg-emerald-100 text-emerald-800'
                          : 'bg-blue-100 text-blue-800'
                      }`}
                    >
                      {enr.completion_status}
                    </span>
                  </div>

                  <p className="text-sm text-slate-600 line-clamp-2">{prog.description}</p>

                  <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                    <div className="flex items-center space-x-1">
                      <UserCheck className="w-3.5 h-3.5 text-slate-400" />
                      <span>Attendance: <strong className="text-slate-700">{enr.attendance_percentage}%</strong></span>
                    </div>

                    {enr.certificate_url && (
                      <a
                        href={enr.certificate_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center text-xs font-semibold text-blue-600 hover:text-blue-800"
                      >
                        <Award className="w-3.5 h-3.5 mr-1" />
                        Certificate
                      </a>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Section 2: Available Training Programs */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
        <h2 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
          <Sparkles className="w-5 h-5 text-blue-600" />
          <span>Available Training Programs ({availablePrograms.length})</span>
        </h2>

        {availablePrograms.length === 0 ? (
          <div className="text-center py-8 bg-slate-50 rounded-xl border border-dashed border-slate-200">
            <Calendar className="w-10 h-10 text-slate-300 mx-auto mb-2" />
            <p className="text-slate-600 font-medium text-sm">No Available Training Programs</p>
            <p className="text-slate-400 text-xs mt-1">You are either enrolled in all available programs or none are scheduled right now.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {availablePrograms.map((prog) => {
              const isEnrolling = enrollingId === prog.id;
              const startDateFormatted = formatDate(prog.start_date);
              const endDateFormatted = formatDate(prog.end_date);
              const dateRangeText = (startDateFormatted || endDateFormatted)
                ? `${startDateFormatted || 'TBD'} - ${endDateFormatted || 'TBD'}`
                : null;

              return (
                <div
                  key={prog.id}
                  className="border border-slate-200 rounded-xl p-5 space-y-3 bg-white hover:border-slate-300 transition-all flex flex-col justify-between"
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between gap-2">
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-50 text-purple-700 border border-purple-100">
                        {prog.program_type || 'BOOTCAMP'}
                      </span>
                      {prog.status && (
                        <span className="text-xs font-semibold text-slate-500 bg-slate-50 px-2 py-0.5 rounded border border-slate-100">
                          {prog.status}
                        </span>
                      )}
                    </div>

                    <h3 className="font-bold text-slate-900 text-base">{prog.title}</h3>
                    <p className="text-sm text-slate-600 line-clamp-2">{prog.description}</p>
                  </div>

                  <div className="pt-3 border-t border-slate-100 space-y-2">
                    <div className="flex flex-wrap items-center justify-between text-xs text-slate-500 gap-2">
                      {dateRangeText && (
                        <div className="flex items-center space-x-1">
                          <Calendar className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                          <span>{dateRangeText}</span>
                        </div>
                      )}
                      {prog.capacity && (
                        <div className="flex items-center space-x-1">
                          <Users className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                          <span>Capacity: <strong>{prog.capacity} Seats</strong></span>
                        </div>
                      )}
                    </div>

                    <div className="flex justify-end pt-1">
                      <Button
                        size="sm"
                        variant="primary"
                        onClick={() => handleEnroll(prog.id, prog.title)}
                        loading={isEnrolling}
                        disabled={isEnrolling || prog.is_enrolled}
                        icon={<GraduationCap className="w-3.5 h-3.5" />}
                      >
                        Enroll
                      </Button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
