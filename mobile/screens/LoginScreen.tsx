import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useAuthStore } from '@stores/authStore';

export default function LoginScreen() {
  const router = useRouter();
  const { login, isLoading, error, clearError } = useAuthStore();
  const [email, setEmail] = useState('professor@escola.com');
  const [password, setPassword] = useState('senha123');

  const handleLogin = async () => {
    if (!email.trim() || !password.trim()) {
      Alert.alert('Erro', 'Por favor, preencha todos os campos');
      return;
    }

    try {
      await login(email, password);
      router.replace('/(app)/home');
    } catch (err) {
      Alert.alert('Erro ao fazer login', error || 'Tente novamente');
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      className="flex-1 bg-gradient-to-b from-blue-50 to-indigo-100"
    >
      <View className="flex-1 justify-center items-center px-6">
        {/* Logo */}
        <View className="mb-8">
          <Text className="text-4xl font-bold text-blue-600 mb-2">
            📚 Pai&Mãe
          </Text>
          <Text className="text-center text-gray-600 text-sm">
            Educação Personalizada
          </Text>
        </View>

        {/* Form */}
        <View className="w-full bg-white rounded-2xl p-6 shadow-lg">
          <Text className="text-2xl font-bold text-gray-900 mb-6">
            Entrar
          </Text>

          {/* Email */}
          <Text className="text-sm font-semibold text-gray-700 mb-2">
            E-mail
          </Text>
          <TextInput
            className="w-full border border-gray-300 rounded-lg px-4 py-3 mb-4 text-gray-900"
            placeholder="seu.email@escola.com"
            value={email}
            onChangeText={setEmail}
            editable={!isLoading}
            keyboardType="email-address"
            autoCapitalize="none"
          />

          {/* Password */}
          <Text className="text-sm font-semibold text-gray-700 mb-2">
            Senha
          </Text>
          <TextInput
            className="w-full border border-gray-300 rounded-lg px-4 py-3 mb-6 text-gray-900"
            placeholder="••••••••"
            value={password}
            onChangeText={setPassword}
            editable={!isLoading}
            secureTextEntry
          />

          {/* Error Message */}
          {error && (
            <View className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
              <Text className="text-sm text-red-700">{error}</Text>
            </View>
          )}

          {/* Login Button */}
          <TouchableOpacity
            onPress={handleLogin}
            disabled={isLoading}
            className={`w-full py-3 rounded-lg flex-row items-center justify-center ${
              isLoading ? 'bg-blue-400' : 'bg-blue-600'
            }`}
          >
            {isLoading ? (
              <ActivityIndicator color="white" />
            ) : (
              <Text className="text-white font-semibold text-base">Entrar</Text>
            )}
          </TouchableOpacity>
        </View>

        {/* Footer */}
        <Text className="text-xs text-gray-500 mt-8 text-center">
          Demo: professor@escola.com / senha123
        </Text>
      </View>
    </KeyboardAvoidingView>
  );
}
