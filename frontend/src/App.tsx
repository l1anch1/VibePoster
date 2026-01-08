/**
 * VibePoster - AI Poster Generator
 * 
 * App 入口文件
 * 负责路由切换（Landing Page / Editor）
 */

import { useState } from 'react';
import { LandingPage, Editor } from './components';

function App() {
  const [showEditor, setShowEditor] = useState(false);

  if (showEditor) {
    return <Editor onBack={() => setShowEditor(false)} />;
  }

  return <LandingPage onEnter={() => setShowEditor(true)} />;
}

export default App;
