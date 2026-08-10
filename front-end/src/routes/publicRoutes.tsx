import type { RouteObject } from "react-router-dom";

import { HomeRedirect, LoginPage, RedirectIfAuthenticated } from "@/auth";
import { PublicLayout } from "../layouts";
import { ROUTE_SEGMENTS, ROUTES } from "./routeConfig";

export const publicRoutes: RouteObject[] = [
    {
        path: ROUTES.HOME,
        element: <HomeRedirect />,
    },
    {
        element: <RedirectIfAuthenticated />,
        children: [
            {
                element: <PublicLayout />,
                children: [
                    {
                        path: ROUTE_SEGMENTS.LOGIN,
                        element: <LoginPage />,
                    },
                ],
            },
        ],
    },
];
