// export default function DocumentViewer({ text = '', sections = [] }) {
//   if (!text) {
//     return (
//       <div className="doc-viewer text-app2 text-sm">
//         No document text available to display.
//       </div>
//     )
//   }

//   // Build highlighted segments from plagiarized_sections
//   const sorted = [...sections].sort(
//     (a, b) => (a.start_char || 0) - (b.start_char || 0)
//   )

//   const segments = []
//   let pos = 0

//   sorted.forEach((sec) => {
//     const start = sec.start_char ?? 0
//     const end   = sec.end_char   ?? start + (sec.text?.length || 60)

//     if (start > pos) {
//       segments.push({ content: text.slice(pos, start), type: 'normal' })
//     }

//     const hlClass =
//       sec.risk === 'High'
//         ? 'hl-high'
//         : sec.risk === 'Medium'
//         ? 'hl-medium'
//         : 'hl-low'

//     segments.push({
//       content: text.slice(start, end) || sec.text || '',
//       type: hlClass,
//       title: sec.source ? `Source: ${sec.source}` : 'Plagiarized section',
//     })
//     pos = end
//   })

//   if (pos < text.length) {
//     segments.push({ content: text.slice(pos), type: 'normal' })
//   }

//   return (
//     <div className="doc-viewer">
//       {segments.map((seg, i) =>
//         seg.type === 'normal' ? (
//           <span key={i}>{seg.content}</span>
//         ) : (
//           <span key={i} className={seg.type} title={seg.title}>
//             {seg.content}
//           </span>
//         )
//       )}
//     </div>
//   )
// }



// export default function DocumentViewer({ text = '', sections = [] }) {
//   if (!text) {
//     return (
//       <div className="doc-viewer text-app2 text-sm">
//         No document text available to display.
//       </div>
//     );
//   }

//   // If no sections are provided, just show the plain text
//   if (!sections || sections.length === 0) {
//     return <div className="doc-viewer whitespace-pre-wrap">{text}</div>;
//   }

//   /**
//    * This function takes the raw text and the list of bad snippets,
//    * then wraps matching parts in a styled span.
//    */
//   const renderHighlightedText = (content, highRiskSections) => {
//     let processedText = content;

//     highRiskSections.forEach((section) => {
//       // Ensure the section is a valid string and not empty
//       const snippet = typeof section === 'string' ? section : section.text;
      
//       if (snippet && snippet.trim().length > 0) {
//         // Escape special characters so Regex doesn't crash on punctuation
//         const escapedSnippet = snippet.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
//         const regex = new RegExp(`(${escapedSnippet})`, 'gi');

//         // We use a CSS class 'hl-high' to stay consistent with your original styles
//         // Or you can use inline styles as shown below
//         processedText = processedText.replace(
//           regex,
//           `<span class="hl-high" style="color: #ef4444; font-weight: bold; background-color: rgba(239, 68, 68, 0.1); cursor: help;" title="High Risk: Direct Match Found">$1</span>`
//         );
//       }
//     });

//     return <div dangerouslySetInnerHTML={{ __html: processedText }} />;
//   };

//   return (
//     <div className="doc-viewer whitespace-pre-wrap leading-relaxed">
//       {renderHighlightedText(text, sections)}
//     </div>
//   );
// }

// 

export default function DocumentViewer({ sections = [] }) {
  // If the backend hasn't found any sections, show a message
  console.log("SECTIONS RECEIVED:", sections);
  if (!sections || sections.length === 0) {
    return (
      <div className="p-8 text-center">
        <div className="text-app2 font-medium">No plagiarism detected.</div>
        <p className="text-app3 text-sm mt-1">This document appears to be original content.</p>
      </div>
    );
  }

  return (
    <div className="document-viewer-content p-6 flex flex-col gap-4">
      <h3 className="text-app font-bold text-sm uppercase tracking-wider mb-2">
        Detected Matches ({sections.length})
      </h3>
      
      {sections.map((sec, index) => {
        const isHigh = sec.risk === 'High' || (sec.similarity && sec.similarity > 0.8);
        
        // Define styles based on risk
        const bgColor = isHigh ? 'rgba(239, 68, 68, 0.1)' : 'rgba(234, 179, 8, 0.1)';
        const borderColor = isHigh ? '#ef4444' : '#ca8a04';
        const textColor = isHigh ? '#ef4444' : '#ca8a04';

        return (
          <div 
            key={index}
            style={{
              backgroundColor: bgColor,
              borderLeft: `4px solid ${borderColor}`,
              padding: '16px',
              borderRadius: '0 8px 8px 0',
              position: 'relative'
            }}
          >
            {/* Risk Badge */}
            <div className="flex justify-between items-center mb-2">
              <span 
                className="text-[10px] font-bold px-2 py-0.5 rounded uppercase"
                style={{ backgroundColor: borderColor, color: '#fff' }}
              >
                {sec.risk || (isHigh ? 'High Risk' : 'Medium Risk')}
              </span>
              {sec.similarity && (
                <span className="text-xs font-mono text-app3">
                  Match: {(sec.similarity * 100).toFixed(1)}%
                </span>
              )}
            </div>

            {/* The actual matching text */}
            <p 
              className="text-sm leading-relaxed whitespace-pre-wrap font-mono"
              style={{ color: 'var(--app-text)' }}
            >
              {/* Clean up the text by removing literal \n strings if they exist */}
              {typeof sec.text === 'string' ? sec.text.replace(/\\n/g, '\n') : 'No text content'}
            </p>
          </div>
        );
      })}
    </div>
  );
}