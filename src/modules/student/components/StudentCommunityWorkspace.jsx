import React, { useState, useEffect, useMemo } from 'react';
import { 
  MessageSquare, 
  Users, 
  Sparkles, 
  Search, 
  Filter, 
  Plus, 
  X, 
  Send, 
  Tag, 
  ThumbsUp, 
  Calendar, 
  Clock, 
  CheckCircle2, 
  AlertCircle, 
  BookOpen, 
  ArrowRight, 
  Share2, 
  MapPin, 
  HelpCircle,
  RefreshCw
} from 'lucide-react';
import api from '../../../lib/api';
import Button from '../../../components/Button';
import Loading from '../../../components/Loading';

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A';
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return String(dateStr);
    return d.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return String(dateStr);
  }
};

export default function StudentCommunityWorkspace() {
  const [activeTab, setActiveTab] = useState('discussions'); // 'discussions' | 'peer-skills' | 'activities'
  
  // Data states
  const [posts, setPosts] = useState([]);
  const [peerSkills, setPeerSkills] = useState([]);
  const [activities, setActivities] = useState([]);
  const [studentSkills, setStudentSkills] = useState([]);
  
  // Status states
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);
  const [successToast, setSuccessToast] = useState(null);

  // Search & Filter
  const [searchTerm, setSearchTerm] = useState('');
  const [postTypeFilter, setPostTypeFilter] = useState('ALL'); // ALL, GENERAL, DISCUSSION, RESOURCE, SHOWCASE
  const [peerSkillFilter, setPeerSkillFilter] = useState('ALL'); // ALL, SEEKING_HELP, OFFERING_HELP

  // Create Post Modal State
  const [createPostModalOpen, setCreatePostModalOpen] = useState(false);
  const [newPostTitle, setNewPostTitle] = useState('');
  const [newPostContent, setNewPostContent] = useState('');
  const [newPostType, setNewPostType] = useState('GENERAL');
  const [newPostTags, setNewPostTags] = useState('');
  const [submittingPost, setSubmittingPost] = useState(false);

  // Comment state (per post)
  const [expandedPostId, setExpandedPostId] = useState(null);
  const [commentText, setCommentText] = useState('');
  const [submittingComment, setSubmittingComment] = useState(false);

  // Create Skill Request Modal State
  const [createSkillModalOpen, setCreateSkillModalOpen] = useState(false);
  const [newSkillId, setNewSkillId] = useState('');
  const [newRequestType, setNewRequestType] = useState('SEEKING_HELP');
  const [newSkillDescription, setNewSkillDescription] = useState('');
  const [submittingSkillRequest, setSubmittingSkillRequest] = useState(false);

  const fetchCommunityData = async () => {
    try {
      setLoading(true);
      setErrorMsg(null);

      // Fetch posts, peer skills, activities, and student skills concurrently
      const [postsRes, peerSkillsRes, activitiesRes, skillsRes] = await Promise.allSettled([
        api.get('/community/posts'),
        api.get('/community/peer-skills'),
        api.get('/community/activities'),
        api.get('/student/skills')
      ]);

      if (postsRes.status === 'fulfilled') {
        setPosts(postsRes.value.data || []);
      } else {
        console.error('Failed to fetch posts:', postsRes.reason);
      }

      if (peerSkillsRes.status === 'fulfilled') {
        setPeerSkills(peerSkillsRes.value.data || []);
      } else {
        console.error('Failed to fetch peer skill requests:', peerSkillsRes.reason);
      }

      if (activitiesRes.status === 'fulfilled') {
        setActivities(activitiesRes.value.data || []);
      } else {
        console.error('Failed to fetch activities:', activitiesRes.reason);
      }

      if (skillsRes.status === 'fulfilled') {
        const sks = skillsRes.value.data || [];
        setStudentSkills(sks);
        if (sks.length > 0 && (sks[0].skill_id || sks[0].id)) {
          setNewSkillId(sks[0].skill_id || sks[0].id);
        }
      }

    } catch (err) {
      console.error('Failed to load community data:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to connect to Community backend service.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCommunityData();
  }, []);

  // Filtered posts
  const filteredPosts = useMemo(() => {
    return posts.filter((p) => {
      const text = `${p.title} ${p.content} ${p.author?.name || ''} ${(p.tags || []).join(' ')}`.toLowerCase();
      const matchesSearch = text.includes(searchTerm.toLowerCase());
      const matchesType = postTypeFilter === 'ALL' || p.post_type === postTypeFilter;
      return matchesSearch && matchesType;
    });
  }, [posts, searchTerm, postTypeFilter]);

  // Filtered peer skills
  const filteredPeerSkills = useMemo(() => {
    return peerSkills.filter((s) => {
      const text = `${s.skill_name} ${s.description} ${s.requester_name} ${s.helper_name || ''}`.toLowerCase();
      const matchesSearch = text.includes(searchTerm.toLowerCase());
      const matchesType = peerSkillFilter === 'ALL' || s.request_type === peerSkillFilter;
      return matchesSearch && matchesType;
    });
  }, [peerSkills, searchTerm, peerSkillFilter]);

  // Create Post Handler
  const handleCreatePost = async (e) => {
    e.preventDefault();
    if (!newPostTitle.trim() || !newPostContent.trim()) {
      setErrorMsg('Post title and content are required.');
      return;
    }

    try {
      setSubmittingPost(true);
      setErrorMsg(null);

      const tagsArray = newPostTags
        .split(',')
        .map(t => t.trim())
        .filter(Boolean);

      const payload = {
        title: newPostTitle.trim(),
        content: newPostContent.trim(),
        post_type: newPostType,
        tags: tagsArray
      };

      const res = await api.post('/community/posts', payload);

      setPosts((prev) => [res.data, ...prev]);
      setSuccessToast('Community post published successfully!');
      setTimeout(() => setSuccessToast(null), 4000);

      // Reset modal
      setCreatePostModalOpen(false);
      setNewPostTitle('');
      setNewPostContent('');
      setNewPostType('GENERAL');
      setNewPostTags('');
    } catch (err) {
      console.error('Failed to create post:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to create community post.');
    } finally {
      setSubmittingPost(false);
    }
  };

  // Create Comment Handler
  const handleAddComment = async (postId) => {
    if (!commentText.trim()) return;

    try {
      setSubmittingComment(true);
      setErrorMsg(null);

      const res = await api.post(`/community/posts/${postId}/comments`, {
        content: commentText.trim()
      });

      // Update local post state
      setPosts((prev) =>
        prev.map((p) => {
          if (p.id === postId) {
            return {
              ...p,
              comments_count: (p.comments_count || 0) + 1,
              comments: [...(p.comments || []), res.data]
            };
          }
          return p;
        })
      );

      setCommentText('');
      setSuccessToast('Comment posted!');
      setTimeout(() => setSuccessToast(null), 3000);
    } catch (err) {
      console.error('Failed to add comment:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to post comment.');
    } finally {
      setSubmittingComment(false);
    }
  };

  // Create Peer Skill Request Handler
  const handleCreateSkillRequest = async (e) => {
    e.preventDefault();
    if (!newSkillDescription.trim()) {
      setErrorMsg('Skill request description is required.');
      return;
    }

    if (!newSkillId && studentSkills.length === 0) {
      setErrorMsg('No skill selected. Please ensure verified skills exist.');
      return;
    }

    try {
      setSubmittingSkillRequest(true);
      setErrorMsg(null);

      const payload = {
        skill_id: newSkillId || studentSkills[0]?.skill_id || studentSkills[0]?.id,
        request_type: newRequestType,
        description: newSkillDescription.trim()
      };

      const res = await api.post('/community/peer-skills', payload);

      setPeerSkills((prev) => [res.data, ...prev]);
      setSuccessToast('Peer skill exchange request published!');
      setTimeout(() => setSuccessToast(null), 4000);

      // Reset modal
      setCreateSkillModalOpen(false);
      setNewSkillDescription('');
    } catch (err) {
      console.error('Failed to create skill request:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to submit skill exchange request.');
    } finally {
      setSubmittingSkillRequest(false);
    }
  };

  if (loading) {
    return <Loading label="Loading Campus Community & Peer Exchange..." />;
  }

  return (
    <div className="space-y-6">
      {/* Toast Notification */}
      {successToast && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 flex items-center justify-between shadow-lg backdrop-blur-md animate-fade-in">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
            <span className="font-medium text-sm">{successToast}</span>
          </div>
          <button onClick={() => setSuccessToast(null)} className="text-emerald-400 hover:text-emerald-300">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Error Alert */}
      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 flex items-center justify-between shadow-lg backdrop-blur-md">
          <div className="flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
            <span className="font-medium text-sm">{errorMsg}</span>
          </div>
          <button onClick={() => setErrorMsg(null)} className="text-rose-400 hover:text-rose-300">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Header / Hero */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border border-indigo-500/20 p-6 md:p-8 shadow-2xl">
        <div className="absolute top-0 right-0 -mt-8 -mr-8 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold uppercase tracking-wider">
              <MessageSquare className="w-3.5 h-3.5" />
              Module 11 — Campus Community & Peer Exchange
            </div>
            <h1 className="text-2xl md:text-3xl font-bold text-white tracking-tight">
              Student Community Workspace
            </h1>
            <p className="text-slate-400 text-sm md:text-base leading-relaxed">
              Connect with fellow peers, engage in domain technical discussions, exchange peer skills, and form project collaboration groups.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3 shrink-0">
            <Button
              variant="outline"
              onClick={fetchCommunityData}
              className="border-slate-700 text-slate-300 hover:bg-slate-800/60"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh Feed
            </Button>
            
            {activeTab === 'discussions' && (
              <Button
                variant="primary"
                onClick={() => setCreatePostModalOpen(true)}
                className="bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/20"
              >
                <Plus className="w-4 h-4 mr-2" />
                New Discussion Post
              </Button>
            )}

            {activeTab === 'peer-skills' && (
              <Button
                variant="primary"
                onClick={() => setCreateSkillModalOpen(true)}
                className="bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/20"
              >
                <Plus className="w-4 h-4 mr-2" />
                New Skill Request
              </Button>
            )}
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="mt-8 pt-6 border-t border-slate-800/80 flex flex-wrap gap-2">
          <button
            onClick={() => setActiveTab('discussions')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-sm transition-all duration-200 ${
              activeTab === 'discussions'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/25 font-semibold'
                : 'bg-slate-800/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            <MessageSquare className="w-4 h-4" />
            Discussion Boards ({posts.length})
          </button>

          <button
            onClick={() => setActiveTab('peer-skills')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-sm transition-all duration-200 ${
              activeTab === 'peer-skills'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/25 font-semibold'
                : 'bg-slate-800/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            <Users className="w-4 h-4" />
            Peer Skill Exchange ({peerSkills.length})
          </button>

          <button
            onClick={() => setActiveTab('activities')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-sm transition-all duration-200 ${
              activeTab === 'activities'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/25 font-semibold'
                : 'bg-slate-800/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            <Calendar className="w-4 h-4" />
            Campus Activities ({activities.length})
          </button>
        </div>
      </div>

      {/* Control Bar (Search & Filter) */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-slate-900/60 border border-slate-800 p-4 rounded-xl backdrop-blur-md">
        <div className="relative w-full sm:w-96">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder={
              activeTab === 'discussions'
                ? 'Search discussions, tags, authors...'
                : activeTab === 'peer-skills'
                ? 'Search skill requests...'
                : 'Search campus activities...'
            }
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-10 pr-4 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
          />
        </div>

        {activeTab === 'discussions' && (
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <Filter className="w-4 h-4 text-slate-400 shrink-0" />
            <span className="text-xs text-slate-400 font-medium hidden md:inline">Type:</span>
            <select
              value={postTypeFilter}
              onChange={(e) => setPostTypeFilter(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-indigo-500"
            >
              <option value="ALL">All Categories</option>
              <option value="GENERAL">General</option>
              <option value="DISCUSSION">Discussion</option>
              <option value="RESOURCE">Resource</option>
              <option value="SHOWCASE">Showcase</option>
            </select>
          </div>
        )}

        {activeTab === 'peer-skills' && (
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <Filter className="w-4 h-4 text-slate-400 shrink-0" />
            <span className="text-xs text-slate-400 font-medium hidden md:inline">Request Type:</span>
            <select
              value={peerSkillFilter}
              onChange={(e) => setPeerSkillFilter(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-indigo-500"
            >
              <option value="ALL">All Requests</option>
              <option value="SEEKING_HELP">Seeking Help</option>
              <option value="OFFERING_HELP">Offering Help</option>
            </select>
          </div>
        )}
      </div>

      {/* TAB 1: DISCUSSION BOARDS */}
      {activeTab === 'discussions' && (
        <div className="space-y-4">
          {filteredPosts.length === 0 ? (
            <div className="text-center py-16 bg-slate-900/40 border border-slate-800/60 rounded-2xl p-8">
              <MessageSquare className="w-12 h-12 text-slate-600 mx-auto mb-3" />
              <h3 className="text-lg font-semibold text-slate-300">No Discussion Posts Found</h3>
              <p className="text-slate-500 text-sm mt-1 max-w-md mx-auto">
                Be the first to start a conversation! Share technical insights, ask questions, or announce campus projects.
              </p>
              <Button
                variant="primary"
                onClick={() => setCreatePostModalOpen(true)}
                className="mt-5 bg-indigo-600 hover:bg-indigo-500"
              >
                <Plus className="w-4 h-4 mr-2" />
                Publish Discussion Post
              </Button>
            </div>
          ) : (
            filteredPosts.map((post) => {
              const isExpanded = expandedPostId === post.id;

              return (
                <div
                  key={post.id}
                  className="bg-slate-900/80 border border-slate-800 hover:border-slate-700/80 rounded-2xl p-6 space-y-4 transition-all duration-200"
                >
                  {/* Header Author Info & Type */}
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center font-bold text-white text-sm shadow-md">
                        {post.author?.name ? post.author.name.charAt(0).toUpperCase() : 'U'}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="font-semibold text-slate-200 text-sm">{post.author?.name || 'Anonymous Student'}</h4>
                          <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-800 text-indigo-400 border border-slate-700">
                            {post.author?.role || 'STUDENT'}
                          </span>
                        </div>
                        <span className="text-xs text-slate-500">{formatDate(post.created_at)}</span>
                      </div>
                    </div>

                    <span className={`px-3 py-1 rounded-full text-xs font-semibold tracking-wide ${
                      post.post_type === 'RESOURCE' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                      post.post_type === 'SHOWCASE' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                      post.post_type === 'DISCUSSION' ? 'bg-purple-500/10 text-purple-400 border border-purple-500/20' :
                      'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                    }`}>
                      {post.post_type}
                    </span>
                  </div>

                  {/* Post Title & Content */}
                  <div className="space-y-2">
                    <h3 className="text-lg font-bold text-white">{post.title}</h3>
                    <p className="text-slate-300 text-sm whitespace-pre-line leading-relaxed">
                      {post.content}
                    </p>
                  </div>

                  {/* Tags */}
                  {post.tags && post.tags.length > 0 && (
                    <div className="flex flex-wrap gap-2 pt-1">
                      {post.tags.map((tag, idx) => (
                        <span key={idx} className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-slate-950 text-slate-400 border border-slate-800 text-xs">
                          <Tag className="w-3 h-3 text-indigo-400" />
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Action Bar & Comment Expansion Toggle */}
                  <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-1.5 text-indigo-400 font-medium">
                        <ThumbsUp className="w-4 h-4" />
                        <span>{post.upvotes_count || 0} Upvotes</span>
                      </div>

                      <button
                        onClick={() => setExpandedPostId(isExpanded ? null : post.id)}
                        className="flex items-center gap-1.5 hover:text-white transition-colors"
                      >
                        <MessageSquare className="w-4 h-4 text-slate-400" />
                        <span>{post.comments_count || (post.comments || []).length} Comments</span>
                      </button>
                    </div>

                    <button
                      onClick={() => setExpandedPostId(isExpanded ? null : post.id)}
                      className="text-indigo-400 hover:text-indigo-300 font-medium"
                    >
                      {isExpanded ? 'Hide Discussion Thread' : 'Join Discussion Thread'}
                    </button>
                  </div>

                  {/* Comment Thread (Expanded) */}
                  {isExpanded && (
                    <div className="mt-4 pt-4 border-t border-slate-800/80 space-y-4 bg-slate-950/60 rounded-xl p-4">
                      <h5 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                        Discussion Replies ({post.comments?.length || 0})
                      </h5>

                      {post.comments && post.comments.length > 0 ? (
                        <div className="space-y-3">
                          {post.comments.map((comment) => (
                            <div key={comment.id} className="bg-slate-900 border border-slate-800/70 rounded-xl p-3 space-y-1">
                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                  <span className="font-semibold text-xs text-slate-200">{comment.author?.name || 'Student'}</span>
                                  <span className="text-[10px] text-slate-500">{formatDate(comment.created_at)}</span>
                                </div>
                              </div>
                              <p className="text-xs text-slate-300 leading-relaxed">{comment.content}</p>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-xs text-slate-500 italic">No responses yet. Write the first reply below.</p>
                      )}

                      {/* Add Comment Form */}
                      <div className="flex items-center gap-2 pt-2">
                        <input
                          type="text"
                          placeholder="Write a constructive response..."
                          value={commentText}
                          onChange={(e) => setCommentText(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') handleAddComment(post.id);
                          }}
                          className="flex-1 bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                        />
                        <Button
                          variant="primary"
                          onClick={() => handleAddComment(post.id)}
                          disabled={submittingComment || !commentText.trim()}
                          className="bg-indigo-600 text-xs px-3 py-2"
                        >
                          <Send className="w-3.5 h-3.5" />
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      )}

      {/* TAB 2: PEER SKILL EXCHANGE */}
      {activeTab === 'peer-skills' && (
        <div className="space-y-4">
          {filteredPeerSkills.length === 0 ? (
            <div className="text-center py-16 bg-slate-900/40 border border-slate-800/60 rounded-2xl p-8">
              <Users className="w-12 h-12 text-slate-600 mx-auto mb-3" />
              <h3 className="text-lg font-semibold text-slate-300">No Peer Skill Requests</h3>
              <p className="text-slate-500 text-sm mt-1 max-w-md mx-auto">
                Connect with study partners or request technical guidance from peers with complementary skills.
              </p>
              <Button
                variant="primary"
                onClick={() => setCreateSkillModalOpen(true)}
                className="mt-5 bg-indigo-600 hover:bg-indigo-500"
              >
                <Plus className="w-4 h-4 mr-2" />
                Post Skill Exchange Request
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredPeerSkills.map((req) => (
                <div
                  key={req.id}
                  className="bg-slate-900/80 border border-slate-800 hover:border-indigo-500/40 rounded-2xl p-6 space-y-4 transition-all duration-200 flex flex-col justify-between"
                >
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-3">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-semibold uppercase tracking-wider ${
                        req.request_type === 'SEEKING_HELP'
                          ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                          : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      }`}>
                        {req.request_type === 'SEEKING_HELP' ? 'Seeking Peer Guidance' : 'Offering Mentorship/Help'}
                      </span>

                      <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-800 text-slate-400 border border-slate-700">
                        {req.status}
                      </span>
                    </div>

                    <div>
                      <h4 className="text-base font-bold text-white flex items-center gap-2">
                        <BookOpen className="w-4 h-4 text-indigo-400" />
                        {req.skill_name || 'Technical Skill'}
                      </h4>
                      <p className="text-xs text-slate-400 mt-1">
                        Posted by <span className="font-semibold text-slate-300">{req.requester_name}</span> • {formatDate(req.created_at)}
                      </p>
                    </div>

                    <p className="text-sm text-slate-300 leading-relaxed bg-slate-950/60 border border-slate-800/80 p-3 rounded-xl">
                      {req.description}
                    </p>
                  </div>

                  <div className="pt-3 border-t border-slate-800 flex items-center justify-between text-xs">
                    <span className="text-slate-500">
                      {req.helper_name ? `Paired Helper: ${req.helper_name}` : 'Open for peer pairing'}
                    </span>
                    <Button
                      variant="outline"
                      onClick={() => {
                        setSuccessToast(`Interest expressed to collaborate with ${req.requester_name}!`);
                        setTimeout(() => setSuccessToast(null), 3000);
                      }}
                      className="border-indigo-500/30 text-indigo-400 hover:bg-indigo-500/10 text-xs py-1.5 px-3"
                    >
                      Collaborate / Connect
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 3: CAMPUS ACTIVITIES & EVENTS */}
      {activeTab === 'activities' && (
        <div className="space-y-4">
          {activities.length === 0 ? (
            <div className="text-center py-16 bg-slate-900/40 border border-slate-800/60 rounded-2xl p-8">
              <Calendar className="w-12 h-12 text-slate-600 mx-auto mb-3" />
              <h3 className="text-lg font-semibold text-slate-300">No Scheduled Campus Activities</h3>
              <p className="text-slate-500 text-sm mt-1 max-w-md mx-auto">
                Check back soon for upcoming campus hackathons, technical workshops, and guest tech talks.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {activities.map((act) => (
                <div
                  key={act.id}
                  className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4"
                >
                  <div className="flex items-start justify-between gap-3">
                    <span className="px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                      {act.activity_type || 'EVENT'}
                    </span>
                    <span className="text-xs text-slate-400 flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5 text-indigo-400" />
                      {formatDate(act.start_time)}
                    </span>
                  </div>

                  <div>
                    <h4 className="text-lg font-bold text-white">{act.title}</h4>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Host: {act.conducted_by_name || act.institution_name || 'Campus Academic Department'}
                    </p>
                  </div>

                  <p className="text-sm text-slate-300 leading-relaxed">
                    {act.description}
                  </p>

                  {act.location_or_url && (
                    <div className="flex items-center gap-2 text-xs text-indigo-400 pt-2 border-t border-slate-800">
                      <MapPin className="w-3.5 h-3.5" />
                      <span>{act.location_or_url}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* MODAL: CREATE DISCUSSION POST */}
      {createPostModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl space-y-5 p-6">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div className="flex items-center gap-2">
                <MessageSquare className="w-5 h-5 text-indigo-400" />
                <h3 className="text-lg font-bold text-white">Publish Discussion Post</h3>
              </div>
              <button
                onClick={() => setCreatePostModalOpen(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreatePost} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Post Title *
                </label>
                <input
                  type="text"
                  placeholder="e.g. Tips for mastering React & Node.js state management"
                  value={newPostTitle}
                  onChange={(e) => setNewPostTitle(e.target.value)}
                  required
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3.5 py-2.5 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                    Category Type *
                  </label>
                  <select
                    value={newPostType}
                    onChange={(e) => setNewPostType(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3.5 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                  >
                    <option value="GENERAL">General</option>
                    <option value="DISCUSSION">Discussion</option>
                    <option value="RESOURCE">Resource</option>
                    <option value="SHOWCASE">Showcase</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                    Tags (Comma-separated)
                  </label>
                  <input
                    type="text"
                    placeholder="react, webdev, python"
                    value={newPostTags}
                    onChange={(e) => setNewPostTags(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3.5 py-2.5 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Detailed Content *
                </label>
                <textarea
                  rows={5}
                  placeholder="Elaborate your question, technical explanation, or resource sharing detail..."
                  value={newPostContent}
                  onChange={(e) => setNewPostContent(e.target.value)}
                  required
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3.5 py-2.5 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 resize-none"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setCreatePostModalOpen(false)}
                  className="border-slate-800 text-slate-300"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  disabled={submittingPost}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white"
                >
                  {submittingPost ? 'Publishing...' : 'Publish Post'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: CREATE PEER SKILL REQUEST */}
      {createSkillModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl space-y-5 p-6">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div className="flex items-center gap-2">
                <Users className="w-5 h-5 text-indigo-400" />
                <h3 className="text-lg font-bold text-white">Post Skill Exchange Request</h3>
              </div>
              <button
                onClick={() => setCreateSkillModalOpen(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateSkillRequest} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Request Intent *
                </label>
                <select
                  value={newRequestType}
                  onChange={(e) => setNewRequestType(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3.5 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="SEEKING_HELP">Seeking Help / Mentorship</option>
                  <option value="OFFERING_HELP">Offering Help / Peer Tutoring</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Associated Technical Skill *
                </label>
                {studentSkills.length > 0 ? (
                  <select
                    value={newSkillId}
                    onChange={(e) => setNewSkillId(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3.5 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                  >
                    {studentSkills.map((sk) => (
                      <option key={sk.skill_id || sk.id} value={sk.skill_id || sk.id}>
                        {sk.skill_name || 'Skill'} ({sk.proficiency_level || 'STUDENT'})
                      </option>
                    ))}
                  </select>
                ) : (
                  <p className="text-xs text-amber-400 bg-amber-500/10 p-2.5 rounded-lg border border-amber-500/20">
                    No verified profile skills detected. Defaulting request to general peer collaboration.
                  </p>
                )}
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Exchange Description & Goals *
                </label>
                <textarea
                  rows={4}
                  placeholder="Describe what specific topic or project module you need help with or want to teach..."
                  value={newSkillDescription}
                  onChange={(e) => setNewSkillDescription(e.target.value)}
                  required
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3.5 py-2.5 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 resize-none"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setCreateSkillModalOpen(false)}
                  className="border-slate-800 text-slate-300"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  disabled={submittingSkillRequest}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white"
                >
                  {submittingSkillRequest ? 'Submitting...' : 'Post Request'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
