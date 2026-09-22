import React from 'react';
import PageContainer from '../components/PageContainer';
import RecommendationWorkspace from '../components/RecommendationWorkspace';

export default function AI() {
  return (
    <PageContainer
      badge="Platform Module"
      title="AI & Intelligent Recommendations"
      subtitle="Skill-aware career role matching, training gap analytics, and opportunity recommendations."
    >
      <RecommendationWorkspace />
    </PageContainer>
  );
}
