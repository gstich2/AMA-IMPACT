# Dependencies Installation Guide

This document tracks all NPM packages that need to be installed for the AMA-IMPACT frontend application.

## Required NPM Packages

### Core Dependencies (should be in package.json)
```bash
npm install next@16.0.1 react react-dom typescript @types/node @types/react @types/react-dom
```

### UI Framework & Components
```bash
npm install @radix-ui/react-dialog
npm install @radix-ui/react-form
npm install @radix-ui/react-select
npm install @radix-ui/react-label
npm install @radix-ui/react-slot
npm install @radix-ui/react-toast
npm install class-variance-authority
npm install clsx
npm install tailwind-merge
```

### Form Handling & Validation
```bash
npm install react-hook-form
npm install @hookform/resolvers
npm install zod
```

### Notifications
```bash
npm install sonner
```

### HTTP Client & Authentication
```bash
npm install axios
```

### Icons
```bash
npm install lucide-react
```

### Development Dependencies
```bash
npm install -D tailwindcss postcss autoprefixer
npm install -D @types/node @types/react @types/react-dom
npm install -D eslint eslint-config-next
```

## Installation Commands

### Full Installation (run this in frontend directory)
```bash
# All dependencies in one command
npm install @radix-ui/react-dialog @radix-ui/react-form @radix-ui/react-select @radix-ui/react-label @radix-ui/react-slot class-variance-authority clsx tailwind-merge react-hook-form @hookform/resolvers zod sonner axios lucide-react

# Or install separately:
# Core UI components
npm install @radix-ui/react-dialog @radix-ui/react-form @radix-ui/react-select @radix-ui/react-label @radix-ui/react-slot class-variance-authority clsx tailwind-merge

# Form handling
npm install react-hook-form @hookform/resolvers zod

# Notifications & HTTP
npm install sonner axios

# Icons
npm install lucide-react
```

## Package.json Equivalent
Unlike Python's requirements.txt, NPM uses package.json to track dependencies. All installed packages are automatically added to package.json when you use `npm install <package>`.

## Verification
After installation, verify all packages are in `package.json`:
```bash
npm list --depth=0
```

## Notes
- This project does NOT use Docker
- All dependencies are managed via NPM/package.json
- UI components use shadcn/ui pattern with Radix UI primitives
- TypeScript is used throughout the project

## Created UI Components
The following shadcn/ui components have been created in `/components/ui/`:
- `dialog.tsx` - Modal dialogs with overlay and close button
- `form.tsx` - Form components with validation and error handling  
- `input.tsx` - Standard input field component
- `label.tsx` - Label component for form fields
- `select.tsx` - Dropdown select component with search
- `textarea.tsx` - Multi-line text input component

## Build Status  
✅ **Frontend builds successfully** with all dependencies installed
✅ **Admin Contracts Management** interface operational
✅ **Toast notifications** working with Sonner
✅ **Form validation** working with React Hook Form + Zod

## Last Updated
November 7, 2025