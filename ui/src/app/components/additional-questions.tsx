import React, { useState } from 'react';
import {
  Box,
  VStack,
  Heading,
  Text,
  Textarea,
  Button,
  useColorModeValue,
  FormControl,
  FormLabel,
  Divider,
} from '@chakra-ui/react';

interface AdditionalQuestionsProps {
  questions: string[];
  onSubmit: (answers: string[]) => void;
  submitButtonText?: string;
}

const AdditionalQuestions: React.FC<AdditionalQuestionsProps> = ({
  questions,
  onSubmit,
  submitButtonText = "Refine Recommendations"
}) => {
  const [answers, setAnswers] = useState<string[]>(Array(questions.length).fill(''));
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('brand.pink', 'brand.purple');
  const textColor = useColorModeValue('gray.700', 'gray.300');

  const handleChange = (index: number, value: string) => {
    const newAnswers = [...answers];
    newAnswers[index] = value;
    setAnswers(newAnswers);
  };

  const handleSubmit = () => {
    const nonEmptyAnswers = answers.map((answer, index) => ({
      question: questions[index],
      answer: answer.trim()
    })).filter(qa => qa.answer !== '');

    onSubmit(nonEmptyAnswers.map(qa => qa.answer));
    // Reset answers after submission
    setAnswers(Array(questions.length).fill(''));
  };

  const isSubmitDisabled = answers.every(answer => !answer || answer.trim() === '');

  return (
    <Box bg={bgColor} p={8} borderRadius="xl" boxShadow="lg" borderWidth={1} borderColor={borderColor}>
      <VStack spacing={6} align="stretch">
        <Heading size="lg" mb={2}>Help Us Refine Your Recommendations</Heading>
        <Text color={textColor} mb={4}>
          Answer at least one question to refine your recommendations. The more information you provide, the better we can tailor your results.
        </Text>
        <Divider mb={4} />
        {questions.map((question, index) => (
          <FormControl key={index}>
            <FormLabel fontWeight="bold" color={textColor}>{question}</FormLabel>
            <Textarea
              value={answers[index]}
              onChange={(e) => handleChange(index, e.target.value)}
              placeholder="Your answer"
              resize="vertical"
              minHeight="100px"
              focusBorderColor="brand.pink"
              _hover={{ borderColor: 'brand.purple' }}
            />
          </FormControl>
        ))}
        <Button
          colorScheme="pink"
          onClick={handleSubmit}
          size="lg"
          mt={4}
          _hover={{ bg: 'brand.purple' }}
          _active={{ bg: 'brand.pink' }}
          isDisabled={isSubmitDisabled}
        >
          {submitButtonText}
        </Button>
      </VStack>
    </Box>
  );
};

export default AdditionalQuestions;
