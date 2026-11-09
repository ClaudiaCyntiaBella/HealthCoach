import React, { useState } from 'react';
import {
  SafeAreaView,
  StyleSheet,
  View,
} from 'react-native';

import LoginScreen from './screens/LoginScreen';
import RegisterScreen from './screens/RegisterScreen';
import HomeScreen from './screens/HomeScreen';
import AnalysisScreen from './screens/AnalysisScreen';
import HistoryScreen from './screens/HistoryScreen';
import HealthProfileScreen from './screens/HealthProfileScreen';
import HealthProfileOverviewScreen from './screens/HealthProfileOverviewScreen';
import BottomNavigation from './components/BottomNavigation';

const MAIN_TABS = ['home', 'analysis', 'history', 'profile'];

export default function App() {
  const [currentScreen, setCurrentScreen] = useState('login');

  const isMainTab = MAIN_TABS.includes(currentScreen);

  const navigate = (screen) => {
    setCurrentScreen(screen);
  };

  const renderScreen = () => {
    switch (currentScreen) {
      case 'login':
        return (
          <LoginScreen
            onGoToRegister={() => navigate('register')}
            onLoginSuccess={() => navigate('home')}
          />
        );

      case 'register':
        return (
          <RegisterScreen
            onBackToLogin={() => navigate('login')}
          />
        );

      case 'home':
        return (
          <HomeScreen
            onLogout={() => navigate('login')}
            onStartAnalysis={() => navigate('analysis')}
          />
        );

      case 'history':
        return (
          <HistoryScreen
            onBack={() => navigate('home')}
          />
        );

      case 'profile':
        return (
          <HealthProfileOverviewScreen
            onEditProfile={() => navigate('healthProfile')}
          />
        );

      case 'healthProfile':
        return (
          <HealthProfileScreen
            onBack={() => navigate('profile')}
          />
        );

      case 'analysis':
        return (
          <AnalysisScreen
            onBack={() => navigate('home')}
          />
        );

      default:
        return (
          <LoginScreen
            onGoToRegister={() => navigate('register')}
            onLoginSuccess={() => navigate('home')}
          />
        );
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.screen}>
        {renderScreen()}
      </View>

      {isMainTab && (
        <SafeAreaView style={styles.navigationSafeArea}>
          <BottomNavigation
            activeTab={currentScreen}
            onNavigate={navigate}
          />
        </SafeAreaView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  screen: {
    flex: 1,
  },
  navigationSafeArea: {
    backgroundColor: '#FFFFFF',
  },
});
