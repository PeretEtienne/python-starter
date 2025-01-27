/*
  Warnings:

  - Added the required column `hashed_password` to the `User` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "User" ADD COLUMN     "hashed_password" TEXT NOT NULL;
