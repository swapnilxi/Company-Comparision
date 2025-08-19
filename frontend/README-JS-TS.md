# Using JavaScript and TypeScript Together in Next.js

This project demonstrates how to effectively use JavaScript and TypeScript together in a Next.js application. This approach allows you to:

- Gradually migrate JavaScript codebases to TypeScript
- Use JavaScript libraries in TypeScript projects
- Use TypeScript features in JavaScript files via JSDoc

## Project Structure

The project includes both JavaScript (`.js`/`.jsx`) and TypeScript (`.ts`/`.tsx`) files working together:

### TypeScript Files

- `src/utils/companyUtils.ts` - TypeScript utility with interfaces and typed functions
- `src/components/CompanyCard.tsx` - React component with TypeScript props interface

### JavaScript Files

- `src/utils/helpers.js` - JavaScript utility functions
- `src/components/ComparisonChart.jsx` - React component in JavaScript
- `src/utils/analytics.js` - JavaScript with JSDoc type annotations

## Key Configuration

### TypeScript Configuration

The `tsconfig.json` file is configured to allow mixed JavaScript and TypeScript:

```json
{
  "compilerOptions": {
    "allowJs": true,
    // Other options...
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx", ".next/types/**/*.ts"]
}
```

Key settings:

- `allowJs: true` - Allows JavaScript files to be compiled
- Include patterns for both `.js`/`.jsx` and `.ts`/`.tsx` files

## Integration Techniques

### 1. Importing JS from TS

TypeScript files can directly import JavaScript files:

```typescript
// In a TypeScript file
import { formatCurrency } from '../utils/helpers.js';
```

### 2. Importing TS from JS

JavaScript files can import from TypeScript files (types are erased at runtime):

```javascript
// In a JavaScript file
import { compareCompanies } from '../utils/companyUtils';
```

### 3. Using TypeScript Types in JavaScript via JSDoc

JavaScript files can use TypeScript types through JSDoc annotations:

```javascript
/** @typedef {import('./companyUtils').CompanyInfo} CompanyInfo */

/**
 * @param {CompanyInfo} company
 */
function processCompany(company) {
  // TypeScript type checking works here!
}
```

## Best Practices

1. **File Extensions**: Always include file extensions in imports for clarity
2. **Type Definitions**: Define interfaces/types in TypeScript files
3. **JSDoc for JS Files**: Use JSDoc comments in JavaScript files for TypeScript integration
4. **Gradual Migration**: Start with critical files when migrating from JS to TS

## Resources

- [Next.js TypeScript Documentation](https://nextjs.org/docs/pages/building-your-application/configuring/typescript)
- [TypeScript Handbook: JSDoc Reference](https://www.typescriptlang.org/docs/handbook/jsdoc-supported-types.html)
- [TypeScript: JavaScript Migration Guide](https://www.typescriptlang.org/docs/handbook/migrating-from-javascript.html)