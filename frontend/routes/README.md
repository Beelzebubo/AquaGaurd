# Routes

TanStack Start uses **file-based routing**. Every `.tsx` file in this directory
is a route. The only root layout is `__root.tsx`.

## Conventions

| File                     | URL                                                     |
| ------------------------ | ------------------------------------------------------- |
| `index.tsx`              | `/`                                                     |
| `hydropower.tsx`         | `/hydropower`                                           |
| `compliance.tsx`         | `/compliance`                                           |
| `stations.tsx`           | `/stations`                                             |
| `__root.tsx`             | app shell — wraps every page; preserve `<Outlet />`     |

`routeTree.gen.ts` is auto-generated. Don't edit it by hand.
