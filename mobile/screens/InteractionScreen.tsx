import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
import { useRoute } from '@react-navigation/native';
import { useRouter } from 'expo-router';
import apiService from '@services/api';

interface Interaction {
  id: string;
  message: string;
  recipient_type: string;
  context_json?: {
    theme?: string;
  };
}

const EMOJI_RATINGS = ['😞', '😐', '🙂', '😊', '🎉'];

export default function InteractionScreen() {
  const route = useRoute<any>();
  const router = useRouter();
  const interactionId = route.params?.id;

  const [interaction, setInteraction] = useState<Interaction | null>(null);
  const [responseText, setResponseText] = useState('');
  const [selectedScore, setSelectedScore] = useState(3);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    loadInteraction();
  }, [interactionId]);

  const loadInteraction = async () => {
    try {
      // TODO: Implementar endpoint para pegar interação individual
      setIsLoading(false);
    } catch (error) {
      console.error('Erro ao carregar interação:', error);
      Alert.alert('Erro', 'Não foi possível carregar a interação');
      setIsLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!responseText.trim()) {
      Alert.alert('Erro', 'Por favor, escreva uma resposta');
      return;
    }

    setIsSubmitting(true);
    try {
      await apiService.respondToInteraction(
        interactionId,
        responseText,
        selectedScore
      );
      setSubmitted(true);
      Alert.alert('Sucesso', 'Resposta enviada!');
      setTimeout(() => {
        router.back();
      }, 1000);
    } catch (error) {
      Alert.alert(
        'Erro',
        error instanceof Error ? error.message : 'Erro ao enviar resposta'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      className="flex-1 bg-gray-50"
    >
      {isLoading ? (
        <View className="flex-1 justify-center items-center">
          <ActivityIndicator size="large" color="#667eea" />
        </View>
      ) : (
        <ScrollView className="flex-1 px-4 py-4">
          {/* Header */}
          <View className="bg-white rounded-xl p-4 mb-4 shadow-sm">
            <Text className="text-lg font-bold text-gray-900 mb-3">
              📨 Responda à Atividade
            </Text>
            <View className="bg-blue-50 p-3 rounded-lg border border-blue-200">
              <Text className="text-gray-700">
                {interaction?.message ||
                  'Qual é sua opinião sobre o assunto abordado?'}
              </Text>
            </View>
          </View>

          {!submitted && (
            <View className="bg-white rounded-xl p-4 shadow-sm">
              {/* Response Text */}
              <Text className="text-sm font-semibold text-gray-700 mb-2">
                Sua Resposta
              </Text>
              <TextInput
                className="w-full border border-gray-300 rounded-lg px-4 py-3 mb-4 text-gray-900"
                placeholder="Escreva sua resposta aqui..."
                value={responseText}
                onChangeText={setResponseText}
                multiline
                numberOfLines={5}
                editable={!isSubmitting}
              />

              {/* Rating */}
              {interaction?.recipient_type === 'child' && (
                <View>
                  <Text className="text-sm font-semibold text-gray-700 mb-3">
                    Como você se avalia? (1-5)
                  </Text>
                  <View className="flex-row justify-between mb-6">
                    {[1, 2, 3, 4, 5].map((score) => (
                      <TouchableOpacity
                        key={score}
                        onPress={() => setSelectedScore(score)}
                        className={`px-4 py-3 rounded-lg border-2 ${
                          selectedScore === score
                            ? 'bg-blue-600 border-blue-600'
                            : 'bg-white border-gray-200'
                        }`}
                        disabled={isSubmitting}
                      >
                        <Text className="text-2xl">
                          {EMOJI_RATINGS[score - 1]}
                        </Text>
                      </TouchableOpacity>
                    ))}
                  </View>
                </View>
              )}

              {/* Submit Button */}
              <TouchableOpacity
                onPress={handleSubmit}
                disabled={isSubmitting || !responseText.trim()}
                className={`w-full py-4 rounded-lg items-center ${
                  isSubmitting || !responseText.trim()
                    ? 'bg-gray-300'
                    : 'bg-blue-600'
                }`}
              >
                {isSubmitting ? (
                  <ActivityIndicator color="white" />
                ) : (
                  <Text className="text-white font-bold text-lg">
                    Enviar Resposta
                  </Text>
                )}
              </TouchableOpacity>
            </View>
          )}

          {submitted && (
            <View className="bg-green-50 border border-green-200 rounded-xl p-6 items-center">
              <Text className="text-4xl mb-3">✓</Text>
              <Text className="text-lg font-bold text-green-700 text-center">
                Resposta Enviada com Sucesso!
              </Text>
              <Text className="text-sm text-gray-600 text-center mt-2">
                Obrigado por sua participação
              </Text>
            </View>
          )}
        </ScrollView>
      )}
    </KeyboardAvoidingView>
  );
}
