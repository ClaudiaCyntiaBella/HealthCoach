
import React, { useState } from 'react';
import { View, StyleSheet } from 'react-native';

import LoginScreen from './screens/LoginScreen';
import RegisterScreen from './screens/RegisterScreen';
import HomeScreen from './screens/HomeScreen';
import AnalysisScreen from './screens/AnalysisScreen';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState('login');

  return (
    <View style={styles.container}>
      {currentScreen === 'login' ? (
        <LoginScreen
          onGoToRegister={() => setCurrentScreen('register')}
          onLoginSuccess={() => setCurrentScreen('home')}
        />
      ) : currentScreen === 'register' ? (
        <RegisterScreen
          onBackToLogin={() => setCurrentScreen('login')}
        />
      ) : currentScreen === 'home' ? (
        <HomeScreen
          onLogout={() => setCurrentScreen('login')}
          onStartAnalysis={() => setCurrentScreen('analysis')}
        />
      ) : (
        <AnalysisScreen onBack={() => setCurrentScreen('home')} />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});
