---
name: docusaurus
description: Provides technical guidance on building documentation sites with Docusaurus. Use when setting up Docusaurus projects, configuring docusaurus.config.js, creating sidebars, working with MDX features, implementing versioning or i18n, customizing themes, or deploying documentation sites.
---

# Building Documentation with Docusaurus

Docusaurus is a static-site generator maintained by Meta that builds single-page React applications optimized for documentation. It uses MDX (Markdown + JSX), provides built-in versioning and i18n, and deploys to any static hosting provider.

## Architecture Overview

Docusaurus follows a plugin-based architecture:

1. **Plugins** collect content (docs, blog, pages) and emit JSON data
2. **Themes** provide React components that render the JSON as pages
3. **Presets** bundle multiple plugins and themes together
4. **SSG** renders React to static HTML for fast loads and SEO

The `@docusaurus/preset-classic` bundles the essential plugins:
- `plugin-content-docs` - Documentation pages
- `plugin-content-blog` - Blog posts
- `plugin-content-pages` - Standalone pages
- `plugin-sitemap` - Sitemap generation
- `theme-classic` - Default theme components

## Project Structure

```
my-docs-site/
├── docs/                     # Documentation markdown/MDX files
├── blog/                     # Blog posts (optional)
├── src/
│   ├── components/           # Custom React components
│   ├── css/                  # Custom stylesheets
│   ├── pages/                # Standalone pages
│   └── theme/                # Swizzled theme components
├── static/                   # Static assets (copied to build/)
├── i18n/                     # Internationalization files
├── versioned_docs/           # Versioned documentation
├── versioned_sidebars/       # Versioned sidebar configs
├── docusaurus.config.js      # Main configuration (or .ts)
├── sidebars.js               # Sidebar structure
└── versions.json             # Available doc versions
```

## Quick Reference

| Task | Details |
|------|---------|
| Configuration | [configuration.md](configuration.md) |
| MDX Features | [mdx-features.md](mdx-features.md) |
| Sidebars & Navigation | [sidebars-navigation.md](sidebars-navigation.md) |
| Versioning & i18n | [versioning-i18n.md](versioning-i18n.md) |
| Theme Customization | [theme-customization.md](theme-customization.md) |
| Deployment | [deployment.md](deployment.md) |

## Minimal Configuration

```typescript
// docusaurus.config.ts
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'My Docs',
  tagline: 'Documentation for my project',
  url: 'https://docs.example.com',
  baseUrl: '/',

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    ['classic', {
      docs: {
        sidebarPath: './sidebars.ts',
        editUrl: 'https://github.com/org/repo/edit/main/',
      },
      blog: false, // Disable if not needed
      theme: {
        customCss: './src/css/custom.css',
      },
    } satisfies Preset.Options],
  ],

  themeConfig: {
    navbar: {
      title: 'My Docs',
      logo: { alt: 'Logo', src: 'img/logo.svg' },
      items: [
        { type: 'docSidebar', sidebarId: 'docs', label: 'Docs', position: 'left' },
        { href: 'https://github.com/org/repo', label: 'GitHub', position: 'right' },
      ],
    },
    footer: {
      style: 'dark',
      copyright: `Copyright © ${new Date().getFullYear()}`,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
```

## Essential Commands

```bash
# Create new site
npx create-docusaurus@latest my-docs classic --typescript

# Development server
npm run start

# Production build
npm run build

# Serve production build locally
npm run serve

# Create new version
npm run docusaurus docs:version 1.0.0

# Swizzle a component (wrap or eject)
npm run swizzle @docusaurus/theme-classic ComponentName -- --wrap
```

## Doc Page Frontmatter

```yaml
---
id: unique-doc-id           # URL slug (defaults to filename)
title: Page Title           # <title> and sidebar label
sidebar_label: Short Label  # Override sidebar text
sidebar_position: 1         # Order in sidebar
description: SEO description for search engines
keywords: [docusaurus, docs]
image: /img/og-image.png    # Open Graph image
slug: /custom-url           # Custom URL path
---
```

## Common Patterns

### Docs-Only Mode
Serve docs at site root (`/` instead of `/docs`):

```typescript
presets: [
  ['classic', {
    docs: { routeBasePath: '/' },
    blog: false,
  }],
],
```

### Multiple Doc Instances
For separate documentation sections (e.g., API docs, tutorials):

```typescript
plugins: [
  ['@docusaurus/plugin-content-docs', {
    id: 'api',
    path: 'api-docs',
    routeBasePath: 'api',
    sidebarPath: './sidebarsApi.js',
  }],
],
```

### Announcement Bar

```typescript
themeConfig: {
  announcementBar: {
    id: 'new-release',
    content: 'New version 2.0 is out! <a href="/blog/release">Read more</a>',
    backgroundColor: '#fafbfc',
    textColor: '#091E42',
    isCloseable: true,
  },
},
```

## Best Practices

1. **Use TypeScript config** - `docusaurus.config.ts` provides type safety and autocompletion
2. **Autogenerate sidebars** - Use `type: 'autogenerated'` with `_category_.json` files
3. **Prefer wrapping over ejecting** - Easier to maintain during upgrades
4. **Set frontmatter descriptions** - Improves SEO and search results
5. **Use semantic headings** - Start with `# H1`, structure with `## H2`, etc.
6. **Enable broken link checking** - Set `onBrokenLinks: 'throw'` to catch issues early
7. **Version strategically** - Only version when necessary (maintenance overhead)
8. **Optimize images** - Use SVG for logos, compress PNGs, lazy-load large images

## Notable Sites Using Docusaurus

| Site | Notable Features |
|------|------------------|
| [React Native](https://reactnative.dev) | Versioning, large-scale |
| [Ionic](https://ionicframework.com/docs) | i18n, versioning, design system |
| [Jest](https://jestjs.io) | i18n, versioning |
| [Supabase](https://supabase.com/docs) | Large documentation |
| [Redux](https://redux.js.org) | Multi-package docs |
| [Algolia DocSearch](https://docsearch.algolia.com) | Search integration |
