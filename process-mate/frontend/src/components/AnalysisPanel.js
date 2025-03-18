import React from 'react';

function AnalysisPanel({ analysis, engineAnalysis, loading }) {
  if (loading) {
    return <div>Loading analysis...</div>;
  }
  
  if (!analysis) {
    return <div>Select a move to see analysis</div>;
  }
  
  // Calculate evaluation bar width
  const getEvalBarWidth = (evaluation) => {
    // Convert evaluation to percentage (range from -5 to +5)
    const clampedEval = Math.max(Math.min(evaluation, 5), -5);
    const percentage = ((clampedEval + 5) / 10) * 100;
    return `${percentage}%`;
  };
  
  return (
    <div className="analysis-content">
      {/* Engine Evaluation Section */}
      {engineAnalysis && (
        <div className="analysis-section">
          <h3 className="subsection-title">Engine Evaluation</h3>
          
          <div className="engine-eval">
            <div className="eval-bar">
              <div 
                className="white-eval" 
                style={{ width: getEvalBarWidth(engineAnalysis.evaluation) }}
              />
            </div>
            <div className="eval-value">
              {engineAnalysis.evaluation > 0 ? '+' : ''}
              {engineAnalysis.evaluation.toFixed(1)}
            </div>
          </div>
          
          <div className="top-moves">
            {engineAnalysis.top_moves.map((move, index) => (
              <div key={index} className="top-move">
                <div className="move-san">{move.move}</div>
                <div className="move-eval">
                  {move.eval > 0 ? '+' : ''}
                  {move.eval.toFixed(1)}
                </div>
                <div className="move-continuation">
                  {move.lines.join(' ')}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Thought Process Analysis */}
      <div className="analysis-section">
        <h3 className="subsection-title">Thought Process</h3>
        
        {/* Tactics */}
        <div className="analysis-subsection">
          <h4>Tactics</h4>
          <ul>
            {analysis.thought_process.tactics.map((tactic, index) => (
              <li key={index}>{tactic}</li>
            ))}
          </ul>
        </div>
        
        {/* Strategy */}
        <div className="analysis-subsection">
          <h4>Strategy</h4>
          <ul>
            {analysis.thought_process.strategy.map((strategy, index) => (
              <li key={index}>{strategy}</li>
            ))}
          </ul>
        </div>
        
        {/* Calculation */}
        <div className="analysis-subsection">
          <h4>Calculation</h4>
          <ul>
            {analysis.thought_process.calculation.map((calc, index) => (
              <li key={index}>{calc}</li>
            ))}
          </ul>
        </div>
        
        {/* Evaluation */}
        <div className="analysis-subsection">
          <h4>Evaluation</h4>
          <p>{analysis.thought_process.evaluation}</p>
        </div>
        
        {/* Plans */}
        <div className="analysis-subsection">
          <h4>Plans</h4>
          <ul>
            {analysis.thought_process.plans.map((plan, index) => (
              <li key={index}>{plan}</li>
            ))}
          </ul>
        </div>
      </div>
      
      {/* Move Analysis */}
      <div className="analysis-section">
        <h3 className="subsection-title">Move Analysis</h3>
        
        <div>
          <p><strong>Move:</strong> {analysis.move_analysis.move}</p>
          <p><strong>Strength:</strong> {analysis.move_analysis.strength}</p>
        </div>
        
        <div className="analysis-subsection">
          <h4>Better Alternatives</h4>
          <ul>
            {analysis.move_analysis.better_alternatives.map((move, index) => (
              <li key={index}>{move}</li>
            ))}
          </ul>
        </div>
        
        <div className="analysis-subsection">
          <h4>Best Continuation</h4>
          <ul>
            {analysis.move_analysis.continuation.map((move, index) => (
              <li key={index}>{move}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

export default AnalysisPanel;