export const isDev = import.meta.env.DEV;

export const isServerSide = typeof window === 'undefined';

export const isClientSide = !isServerSide;
