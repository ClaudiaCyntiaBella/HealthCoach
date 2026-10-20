
import React, { useState } from 'react';
import { View, StyleSheet } from 'react-native';

import LoginScreen from './screens/LoginScreen';
import RegisterScreen from './screens/RegisterScreen';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState('login');

  return (
    <View style={styles.container}>
      {currentScreen === 'login' ? (
        <LoginScreen
          onGoToRegister={() => setCurrentScreen('register')}
        />
      ) : (
        <RegisterScreen
          onBackToLogin={() => setCurrentScreen('login')}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});
