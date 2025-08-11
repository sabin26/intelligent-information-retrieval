export enum AppStatus {
  Intro = 'INTRO',
  Task1 = 'TASK_1',
  Task2 = 'TASK_2',
  Complete = 'COMPLETE',
}

export enum ChallengeType {
  Search = 'SEARCH',
  Classify = 'CLASSIFY',
}

export enum DocCategory {
  Politics = 'Politics',
  Business = 'Business',
  Health = 'Health',
  Unknown = 'Unknown',
}

export enum IndexingStrategy {
  Inverted = 'INVERTED',
  Positional = 'POSITIONAL',
}

export interface Author {
  name: string;
  profileUrl?: string;
}

export interface Publication {
  title: string;
  authors: Author[];
  year: string;
  publicationUrl: string;
  relevancyScore?: number;
}

// --- Task-specific interfaces ---

export interface Task1Data {
  prompt: string;
  expectedKeywords: string[];
  mockPublications: Publication[];
}

export interface TaskData {
  id: string;
  title: string;
  description: string;
  task1: Task1Data;
}

// --- Legacy types for unused components to resolve compile errors ---

export interface Challenge {
  type: ChallengeType;
}

export interface Case {
  title: string;
  challenges: Challenge[];
}

export enum AppTab {
  Search = 'SEARCH',
  Classifier = 'CLASSIFIER',
}

export interface ClassificationResult {
  category: DocCategory;
  confidence?: number;
}

export interface WebChunk {
  uri: string;
  title: string;
}

export interface GroundingChunk {
  web?: WebChunk;
}

export interface GroundingMetadata {
  groundingChunks?: GroundingChunk[];
}