import type { HealthRecommendations, Category } from "../../../types/HealthRecommendations";
import type { Progress, CategoryProgress } from "../../../types/Progress";
export default function calculateProgress(healthData: HealthRecommendations) {
    const categories = healthData.categories;
    const categoryProgress: Record<string, CategoryProgress> = {};
    let totalProgress = 0;
    let totalActivities = 0;
    categories.forEach((category) => {
        categoryProgress[category.category_name] = calculateCategoryProgress(category);
        totalProgress += categoryProgress[category.category_name].progress;
        totalActivities += categoryProgress[category.category_name].totalActivities;
    });


    const progress = {
        overallProgress: (totalProgress / totalActivities) * 100,
        categoryProgress: categoryProgress
    } as Progress
    console.log(progress)
    return progress
}

function calculateCategoryProgress(category: Category): CategoryProgress {
    const totalActivities = category.activities.length;
    const completedActivities = category.activities.reduce(
        (sum: number, activity) => {
            if (activity.status === 'Completed') {
                return sum + 1;
            }
            else if (activity.status === 'Partially completed') {
                return sum + 0.5;
            }
            return sum;
        }, 0
    );
    return {
        progress: completedActivities,
        totalActivities: totalActivities
    } as CategoryProgress
}