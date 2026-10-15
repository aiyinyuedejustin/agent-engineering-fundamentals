/* Paste this read-only expression in the console of one standalone fixture. */
(() => {
  const rgb = value => `rgb(${value.join(', ')})`;
  const expectations = document.getElementById('dark-root') ? {
    'dark-root': { backgroundColor: rgb([241, 173, 165]) },
    'dark-child': { backgroundColor: rgb([241, 173, 165]) },
    'dark-no-class': { backgroundColor: 'rgba(0, 0, 0, 0)' },
    'light-root': { backgroundColor: rgb([244, 246, 239]) },
    'light-child': { backgroundColor: rgb([244, 246, 239]) },
    'nested-dark-root': { backgroundColor: rgb([241, 173, 165]) },
    'nested-dark-child': { backgroundColor: rgb([241, 173, 165]) },
    'default-root': { backgroundColor: rgb([248, 247, 243]) },
    'default-child': { backgroundColor: rgb([248, 247, 243]) },
    'invalid-root': { backgroundColor: rgb([248, 247, 243]) },
    'invalid-child': { backgroundColor: rgb([248, 247, 243]) },
    'outside': { backgroundColor: 'rgba(0, 0, 0, 0)' },
    'foreign-ui': { backgroundColor: 'rgba(0, 0, 0, 0)' }
  } : {
    'paper-light': { backgroundColor: rgb([248, 247, 243]), color: rgb([38, 37, 31]) },
    'sage-dark': { backgroundColor: rgb([25, 32, 26]), color: rgb([233, 238, 229]) },
    'ocean-light': { backgroundColor: rgb([243, 246, 247]), color: rgb([34, 50, 58]) },
    'plum-dark': { backgroundColor: rgb([38, 28, 36]), color: rgb([241, 232, 239]) },
    'action': { backgroundColor: rgb([39, 39, 34]), color: rgb([255, 255, 255]), borderRadius: '8px', minHeight: '40px' },
    'card': { borderRadius: '14px' },
    'composer': { borderRadius: '20px' },
    'custom-local': { backgroundColor: rgb([1, 2, 3]), fontFamily: 'monospace', borderRadius: '17px' },
    'outside-box': { boxSizing: 'content-box' },
    'outside-list': { listStyleType: 'disc' }
  };
  const checks = [];
  for (const [id, values] of Object.entries(expectations)) {
    const node = document.getElementById(id);
    for (const [property, expected] of Object.entries(values)) {
      const actual = node ? getComputedStyle(node)[property] : null;
      checks.push({ id, property, expected, actual, passed: actual === expected });
    }
  }
  if (document.getElementById('outside-heading')) {
    const css = getComputedStyle(document.getElementById('outside-heading'));
    checks.push({ id: 'outside-heading', property: 'marginBlockStart > 0', actual: css.marginBlockStart, passed: parseFloat(css.marginBlockStart) > 0 });
  }
  return { passed: checks.every(c => c.passed), userAgent: navigator.userAgent, scopeApiPresent: typeof CSSScopeRule !== 'undefined', checks };
})()
