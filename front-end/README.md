# Frontend

Frontend application built using React, TypeScript and Vite following the CDIS engineering standards.

---

## Technology Stack

- React
- TypeScript
- Vite
- React Router
- React Hook Form
- Zod
- Axios
- Context API

---

## Project Structure

```text
src/
├── app/
├── auth/
├── assets/
├── components/
├── config/
├── features/
├── layouts/
├── routes/
├── shared/
├── styles/
└── main.tsx
```

---

## Install

```bash
npm install
```

---

## Development

Start development server.

```bash
npm run dev
```

---

## Build

```bash
npm run build
```

---

## Preview Production Build

```bash
npm run preview
```

---

## Lint

```bash
npm run lint
```

---

## Development Workflow

When adding a new feature:

1. Create feature module.
2. Create API layer.
3. Create service layer.
4. Create hooks.
5. Create components.
6. Create page.
7. Add route.
8. Add tests.
9. Update documentation.

---

## Frontend Standards

- Feature-first architecture
- TypeScript Strict Mode
- Functional Components
- Custom Hooks for business logic
- Presentational Components for UI
- React Hook Form + Zod for forms
- Axios for API communication
- Context only for global application state
- Absolute imports using aliases

See:

- `../docs/architecture/frontend.md`
- `../docs/standards/code-style.md`
- `../docs/standards/naming-conventions.md`

---

## Testing

Run frontend tests.

```bash
npm test
```

Run coverage.

```bash
npm run test:coverage
```

---

## References

- React — https://react.dev
- TypeScript — https://www.typescriptlang.org
- Vite — https://vite.dev
- React Router — https://reactrouter.com
- React Hook Form — https://react-hook-form.com
- Zod — https://zod.dev
- Axios — https://axios-http.com