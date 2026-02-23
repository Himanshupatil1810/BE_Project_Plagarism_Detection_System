export function generateMockResult(filename, userId) {
  const id = `PLAG_${Date.now()}_${Math.random().toString(36).slice(2, 8).toUpperCase()}`
  const score = parseFloat((Math.random() * 0.85).toFixed(4))

  return {
    report_id: id,
    id,
    user_id: userId,
    status: 'completed',
    overall_similarity_score: score,
    timestamp: new Date().toISOString(),
    filename,
    sources:
      score > 0.08
        ? [
            {
              url: 'https://en.wikipedia.org/wiki/Machine_learning',
              source: 'Wikipedia – Machine Learning',
              similarity: score * 0.9,
              matched_text:
                'Machine learning is a method of data analysis that automates analytical model building based on the idea that systems can learn from data.',
            },
            {
              url: 'https://arxiv.org/abs/2103.00020',
              source: 'arXiv:2103.00020',
              similarity: score * 0.55,
              matched_text:
                'Deep neural networks have demonstrated remarkable performance on a variety of benchmark tasks.',
            },
            {
              url: 'https://towardsdatascience.com/intro-to-ai',
              source: 'Towards Data Science',
              similarity: score * 0.3,
              matched_text:
                'Artificial intelligence encompasses machine learning, natural language processing, and computer vision.',
            },
          ].filter((s) => s.similarity > 0.04)
        : [],
    plagiarized_sections:
      score > 0.2
        ? [
            { start_char: 45,  end_char: 155, risk: score > 0.6 ? 'High' : 'Medium', source: 'Wikipedia' },
            { start_char: 230, end_char: 320, risk: 'Low',                            source: 'arXiv' },
          ]
        : [],
    document_text:
      'Introduction to Machine Learning and AI. ' +
      'Machine learning is a method of data analysis that automates analytical model building based on the idea that systems can learn from data. ' +
      'It is based on the idea that systems can identify patterns and make decisions with minimal human intervention. ' +
      'Deep neural networks have demonstrated remarkable performance on a variety of benchmark tasks in recent years. ' +
      'Artificial intelligence encompasses machine learning, natural language processing, and computer vision among other subfields.',
    blockchain_data: {
      transaction_hash: `0x${Array.from({ length: 64 }, () =>
        Math.floor(Math.random() * 16).toString(16)).join('')}`,
      ipfs_cid: `Qm${Array.from(
        { length: 44 },
        () => 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz123456789'[
          Math.floor(Math.random() * 58)
        ]
      ).join('')}`,
      block_number: Math.floor(Math.random() * 1_000_000) + 18_000_000,
    },
  }
}

export function saveToHistory(userId, result) {
  const key = `chainguard_history_${userId}`
  const prev = JSON.parse(localStorage.getItem(key) || '[]')
  prev.unshift({ ...result, _savedAt: new Date().toISOString() })
  localStorage.setItem(key, JSON.stringify(prev.slice(0, 100)))
}

export function loadHistory(userId) {
  const key = `chainguard_history_${userId}`
  try { return JSON.parse(localStorage.getItem(key) || '[]') }
  catch { return [] }
}
