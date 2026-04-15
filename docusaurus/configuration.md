# Docusaurus Configuration

The `docusaurus.config.js` (or `.ts`) file is the central configuration hub. It's run in Node.js and should export a config object or a function that creates one.

## Configuration File Formats

```typescript
// docusaurus.config.ts (recommended)
import type {Config} from '@docusaurus/types';

const config: Config = {
  // ...
};

export default config;
```

```javascript
// docusaurus.config.js (CommonJS)
module.exports = {
  // ...
};
```

```javascript
// docusaurus.config.js (ESM)
export default {
  // ...
};
```

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `title` | `string` | Site title (appears in browser tab, navbar) |
| `url` | `string` | Production URL (e.g., `https://docs.example.com`) |
| `baseUrl` | `string` | Base path (e.g., `/` or `/docs/`) |

## Common Fields

```typescript
const config: Config = {
  // Required
  title: 'My Documentation',
  url: 'https://docs.example.com',
  baseUrl: '/',

  // Metadata
  tagline: 'Documentation that developers love',
  favicon: 'img/favicon.ico',
  organizationName: 'my-org',      // GitHub org/user
  projectName: 'my-project',       // GitHub repo name

  // Behavior
  onBrokenLinks: 'throw',          // 'ignore' | 'log' | 'warn' | 'throw'
  onBrokenMarkdownLinks: 'warn',
  onDuplicateRoutes: 'warn',

  // Internationalization
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'fr', 'ja'],
    localeConfigs: {
      en: { label: 'English', htmlLang: 'en-US' },
      fr: { label: 'Français', htmlLang: 'fr-FR' },
    },
  },

  // Build
  trailingSlash: false,            // URL trailing slashes
  noIndex: false,                  // Block search engine indexing
  staticDirectories: ['static'],   // Additional static asset dirs
};
```

## Presets Configuration

Presets bundle plugins and themes. `@docusaurus/preset-classic` is the standard choice:

```typescript
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  presets: [
    ['classic', {
      // @docusaurus/plugin-content-docs
      docs: {
        path: 'docs',
        sidebarPath: './sidebars.ts',
        editUrl: 'https://github.com/org/repo/edit/main/',
        showLastUpdateAuthor: true,
        showLastUpdateTime: true,
        breadcrumbs: true,
        routeBasePath: 'docs',    // Use '/' for docs-only mode
      },

      // @docusaurus/plugin-content-blog
      blog: {
        path: 'blog',
        routeBasePath: 'blog',
        showReadingTime: true,
        blogTitle: 'Blog',
        blogDescription: 'Latest updates',
        postsPerPage: 10,
        blogSidebarTitle: 'Recent posts',
        blogSidebarCount: 5,
        feedOptions: {
          type: ['rss', 'atom'],
          copyright: `Copyright © ${new Date().getFullYear()}`,
        },
      },

      // @docusaurus/plugin-content-pages
      pages: {
        path: 'src/pages',
      },

      // @docusaurus/theme-classic
      theme: {
        customCss: './src/css/custom.css',
      },

      // @docusaurus/plugin-sitemap
      sitemap: {
        changefreq: 'weekly',
        priority: 0.5,
        filename: 'sitemap.xml',
      },

      // @docusaurus/plugin-google-gtag
      gtag: {
        trackingID: 'G-XXXXXXXXXX',
        anonymizeIP: true,
      },
    } satisfies Preset.Options],
  ],
};
```

## Theme Configuration

The `themeConfig` object configures the visual appearance:

```typescript
const config: Config = {
  themeConfig: {
    // Color mode
    colorMode: {
      defaultMode: 'light',
      disableSwitch: false,
      respectPrefersColorScheme: true,
    },

    // Navbar
    navbar: {
      title: 'My Docs',
      logo: {
        alt: 'Site Logo',
        src: 'img/logo.svg',
        srcDark: 'img/logo-dark.svg',  // Dark mode logo
        href: '/',
        width: 32,
        height: 32,
      },
      hideOnScroll: false,
      style: 'primary',  // 'primary' | 'dark'
      items: [
        // Doc link
        {
          type: 'docSidebar',
          sidebarId: 'docs',
          position: 'left',
          label: 'Docs',
        },
        // External link
        {
          href: 'https://github.com/org/repo',
          label: 'GitHub',
          position: 'right',
        },
        // Dropdown
        {
          type: 'dropdown',
          label: 'Community',
          position: 'left',
          items: [
            { label: 'Discord', href: 'https://discord.gg/...' },
            { label: 'Twitter', href: 'https://twitter.com/...' },
          ],
        },
        // Version dropdown
        { type: 'docsVersionDropdown', position: 'right' },
        // Locale dropdown
        { type: 'localeDropdown', position: 'right' },
        // Search
        { type: 'search', position: 'right' },
      ],
    },

    // Footer
    footer: {
      style: 'dark',  // 'light' | 'dark'
      logo: {
        alt: 'Logo',
        src: 'img/logo.svg',
        href: '/',
        width: 64,
        height: 64,
      },
      links: [
        {
          title: 'Docs',
          items: [
            { label: 'Getting Started', to: '/docs/intro' },
            { label: 'API Reference', to: '/docs/api' },
          ],
        },
        {
          title: 'Community',
          items: [
            { label: 'Discord', href: 'https://discord.gg/...' },
            { label: 'Stack Overflow', href: 'https://stackoverflow.com/...' },
          ],
        },
        {
          title: 'More',
          items: [
            { label: 'Blog', to: '/blog' },
            { label: 'GitHub', href: 'https://github.com/org/repo' },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} My Company. Built with Docusaurus.`,
    },

    // Table of contents
    tableOfContents: {
      minHeadingLevel: 2,
      maxHeadingLevel: 3,
    },

    // Announcement bar
    announcementBar: {
      id: 'announcement',
      content: 'New version available! <a href="/blog/release">Learn more</a>',
      backgroundColor: '#fafbfc',
      textColor: '#091E42',
      isCloseable: true,
    },

    // Prism syntax highlighting
    prism: {
      theme: require('prism-react-renderer').themes.github,
      darkTheme: require('prism-react-renderer').themes.dracula,
      additionalLanguages: ['bash', 'diff', 'json', 'go', 'rust'],
    },
  } satisfies Preset.ThemeConfig,
};
```

## Search Configuration

### Algolia DocSearch (Recommended)

```typescript
themeConfig: {
  algolia: {
    appId: 'YOUR_APP_ID',
    apiKey: 'YOUR_SEARCH_API_KEY',  // Public key, safe to commit
    indexName: 'YOUR_INDEX_NAME',
    contextualSearch: true,
    searchPagePath: 'search',
  },
},
```

### Local Search (Alternative)

```bash
npm install @easyops-cn/docusaurus-search-local
```

```typescript
themes: [
  ['@easyops-cn/docusaurus-search-local', {
    hashed: true,
    language: ['en'],
  }],
],
```

## SEO Configuration

```typescript
const config: Config = {
  // Global metadata
  themeConfig: {
    metadata: [
      { name: 'keywords', content: 'documentation, api, sdk' },
      { name: 'twitter:card', content: 'summary_large_image' },
    ],
    image: 'img/social-card.png',  // Default OG image
  },

  // Custom head tags
  headTags: [
    {
      tagName: 'link',
      attributes: { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
    },
    {
      tagName: 'script',
      attributes: { type: 'application/ld+json' },
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org/',
        '@type': 'Organization',
        name: 'My Company',
        url: 'https://example.com',
      }),
    },
  ],
};
```

## Plugin Configuration

### Adding Additional Plugins

```typescript
const config: Config = {
  plugins: [
    // PWA support
    ['@docusaurus/plugin-pwa', {
      offlineModeActivationStrategies: ['appInstalled', 'standalone', 'queryString'],
      pwaHead: [
        { tagName: 'link', rel: 'manifest', href: '/manifest.json' },
        { tagName: 'meta', name: 'theme-color', content: '#25c2a0' },
      ],
    }],

    // Ideal Image optimization
    ['@docusaurus/plugin-ideal-image', {
      quality: 70,
      max: 1030,
      min: 640,
      steps: 2,
    }],

    // Multiple docs instances
    ['@docusaurus/plugin-content-docs', {
      id: 'api',
      path: 'api-docs',
      routeBasePath: 'api',
      sidebarPath: './sidebarsApi.js',
    }],

    // Custom plugin (inline)
    function customPlugin(context, options) {
      return {
        name: 'custom-plugin',
        async loadContent() { /* ... */ },
        async contentLoaded({content, actions}) { /* ... */ },
      };
    },
  ],
};
```

## Environment Variables

Access environment variables in config:

```typescript
const config: Config = {
  customFields: {
    apiEndpoint: process.env.API_ENDPOINT || 'https://api.example.com',
  },

  themeConfig: {
    algolia: {
      appId: process.env.ALGOLIA_APP_ID,
      apiKey: process.env.ALGOLIA_API_KEY,
      indexName: process.env.ALGOLIA_INDEX_NAME,
    },
  },
};
```

Access in components:

```jsx
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';

function MyComponent() {
  const { siteConfig } = useDocusaurusContext();
  const { apiEndpoint } = siteConfig.customFields;
  // ...
}
```

## Async Configuration

For dynamic configuration:

```typescript
import type {Config} from '@docusaurus/types';

export default async function createConfig(): Promise<Config> {
  const response = await fetch('https://api.example.com/config');
  const data = await response.json();

  return {
    title: data.title,
    // ...
  };
}
```
