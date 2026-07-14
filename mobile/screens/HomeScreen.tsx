import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useAuthStore } from '@stores/authStore';
import { useLearningStore } from '@stores/learningStore';
import apiService from '@services/api';

interface Child {
  id: string;
  full_name: string;
  grade: string;
}

interface Interaction {
  id: string;
  message: string;
  status: string;
  recipient_type: string;
}

export default function HomeScreen() {
  const router = useRouter();
  const { user, logout } = useAuthStore();
  const { metrics, fetchMetrics, isLoading } = useLearningStore();
  const [children, setChildren] = useState<Child[]>([]);
  const [selectedChild, setSelectedChild] = useState<Child | null>(null);
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (selectedChild) {
      fetchMetrics(selectedChild.id);
      loadInteractions(selectedChild.id);
    }
  }, [selectedChild]);

  const loadData = async () => {
    try {
      const childList = await apiService.getChildren();
      setChildren(childList);
      if (childList.length > 0) {
        setSelectedChild(childList[0]);
      }
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    }
  };

  const loadInteractions = async (childId: string) => {
    try {
      const list = await apiService.getInteractions(childId, 5);
      setInteractions(list);
    } catch (error) {
      console.error('Erro ao carregar interações:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    try {
      await loadData();
      if (selectedChild) {
        await fetchMetrics(selectedChild.id);
        await loadInteractions(selectedChild.id);
      }
    } finally {
      setRefreshing(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    router.replace('/(auth)/login');
  };

  return (
    <View className="flex-1 bg-gray-50">
      {/* Header */}
      <View className="bg-white border-b border-gray-200 px-4 py-4">
        <View className="flex-row justify-between items-center mb-4">
          <View>
            <Text className="text-sm text-gray-600">Bem-vindo,</Text>
            <Text className="text-xl font-bold text-gray-900">{user?.name}</Text>
          </View>
          <TouchableOpacity
            onPress={handleLogout}
            className="bg-red-100 px-3 py-2 rounded-lg"
          >
            <Text className="text-red-600 font-semibold text-sm">Sair</Text>
          </TouchableOpacity>
        </View>

        {/* Child Selector */}
        {children.length > 0 && (
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            className="mb-2"
          >
            {children.map((child) => (
              <TouchableOpacity
                key={child.id}
                onPress={() => setSelectedChild(child)}
                className={`mr-2 px-4 py-2 rounded-full border-2 ${
                  selectedChild?.id === child.id
                    ? 'bg-blue-600 border-blue-600'
                    : 'bg-white border-gray-200'
                }`}
              >
                <Text
                  className={`font-semibold text-sm ${
                    selectedChild?.id === child.id
                      ? 'text-white'
                      : 'text-gray-700'
                  }`}
                >
                  {child.full_name}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        )}
      </View>

      {/* Content */}
      <ScrollView
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        className="flex-1 px-4 py-4"
      >
        {isLoading ? (
          <View className="flex-1 justify-center items-center py-20">
            <ActivityIndicator size="large" color="#667eea" />
          </View>
        ) : selectedChild && metrics ? (
          <View className="space-y-4">
            {/* Métricas */}
            <View className="bg-white rounded-xl p-4 shadow-sm">
              <Text className="text-lg font-bold text-gray-900 mb-4">
                📊 Seu Progresso
              </Text>
              <View className="flex-row justify-between mb-4">
                <View className="flex-1 bg-blue-50 rounded-lg p-3 mr-2">
                  <Text className="text-xs text-gray-600">Taxa de Sucesso</Text>
                  <Text className="text-2xl font-bold text-blue-600">
                    {Math.round(metrics.overall_success_rate * 100)}%
                  </Text>
                </View>
                <View className="flex-1 bg-green-50 rounded-lg p-3">
                  <Text className="text-xs text-gray-600">Engajamento</Text>
                  <Text className="text-2xl font-bold text-green-600">
                    {metrics.average_engagement.toFixed(1)}/5
                  </Text>
                </View>
              </View>

              {/* Risco de Dropout */}
              <View className={`rounded-lg p-3 ${
                metrics.dropout_risk === 'high'
                  ? 'bg-red-50'
                  : metrics.dropout_risk === 'medium'
                  ? 'bg-yellow-50'
                  : 'bg-green-50'
              }`}>
                <Text className="text-xs text-gray-600">Risco de Dropout</Text>
                <Text className={`text-lg font-bold ${
                  metrics.dropout_risk === 'high'
                    ? 'text-red-600'
                    : metrics.dropout_risk === 'medium'
                    ? 'text-yellow-600'
                    : 'text-green-600'
                }`}>
                  {metrics.dropout_risk === 'high'
                    ? 'Alto'
                    : metrics.dropout_risk === 'medium'
                    ? 'Médio'
                    : 'Baixo'}
                </Text>
              </View>
            </View>

            {/* Temas */}
            {metrics.themes_mastered.length > 0 && (
              <View className="bg-white rounded-xl p-4 shadow-sm">
                <Text className="text-lg font-bold text-gray-900 mb-3">
                  ✓ Temas Dominados
                </Text>
                <View className="flex-row flex-wrap gap-2">
                  {metrics.themes_mastered.map((theme) => (
                    <View
                      key={theme}
                      className="bg-green-100 px-3 py-2 rounded-full"
                    >
                      <Text className="text-sm text-green-700 font-semibold">
                        {theme}
                      </Text>
                    </View>
                  ))}
                </View>
              </View>
            )}

            {/* Interações Pendentes */}
            {interactions.length > 0 && (
              <View className="bg-white rounded-xl p-4 shadow-sm">
                <Text className="text-lg font-bold text-gray-900 mb-3">
                  📬 Interações Pendentes ({interactions.length})
                </Text>
                {interactions.map((interaction) => (
                  <TouchableOpacity
                    key={interaction.id}
                    onPress={() =>
                      router.push({
                        pathname: '/(app)/interaction',
                        params: { id: interaction.id },
                      })
                    }
                    className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-2"
                  >
                    <Text className="text-sm text-gray-700 mb-2">
                      {interaction.message}
                    </Text>
                    <Text className="text-xs text-blue-600 font-semibold">
                      Responder →
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            )}

            {/* Action Buttons */}
            <View className="flex-row gap-2 mb-4">
              <TouchableOpacity
                onPress={() => router.push('/(app)/analytics')}
                className="flex-1 bg-blue-600 rounded-lg p-4 items-center"
              >
                <Text className="text-white font-semibold">📊 Analytics</Text>
              </TouchableOpacity>
              <TouchableOpacity
                onPress={() => router.push('/(app)/profile')}
                className="flex-1 bg-purple-600 rounded-lg p-4 items-center"
              >
                <Text className="text-white font-semibold">👤 Perfil</Text>
              </TouchableOpacity>
            </View>
          </View>
        ) : (
          <View className="flex-1 justify-center items-center py-20">
            <Text className="text-gray-500">Nenhuma criança selecionada</Text>
          </View>
        )}
      </ScrollView>
    </View>
  );
}
