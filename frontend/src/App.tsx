/**
 * VibePoster - AI Poster Generator
 * 
 * App 入口文件
 * 负责路由切换（Landing Page / Editor）
 */

import { useState } from 'react';
import { LandingPage, Editor } from './components';
import { ENABLE_LANDING_PAGE } from './config';

function App() {
  const [showEditor, setShowEditor] = useState(!ENABLE_LANDING_PAGE);

  if (showEditor) {
    return <Editor onBack={ENABLE_LANDING_PAGE ? () => setShowEditor(false) : undefined} />;
  }

  return <LandingPage onEnter={() => setShowEditor(true)} />;
}

export default App;
