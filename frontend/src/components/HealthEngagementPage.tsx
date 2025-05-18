import { useEffect, useState } from 'react';
import { fetchHealthData } from '../services/fetchHealthData';
import type { HealthRecommendations, Category, ActivityItem } from '../types/HealthRecommendations';

function HealthEngagementPage() {

    const [data, setData] = useState<HealthRecommendations | null>(null);

    useEffect(() => {
        const loadData = async () => {
            const healthData = await fetchHealthData();
            setData(healthData);
        };

        loadData();
    }, []);

    if (!data) return <LoadingPlaceholder />;

    return (
        <div>
            <div className="scoreCard">
                <ScoreDial />
                <h1>Health Engagement Page</h1>
                <p>Your health engagement score shows key factors involved in your health</p>
            </div>
            <div className="categoryList">
                {data.categories.map((category) => (
                    <CategoryListItem
                        key={category.category_name}
                        categoryData={category}
                    />
                ))}
            </div>


        </div>
    );
}

function ScoreDial() {
    return (
        <p>
            Score dial here
        </p>
    )
}

function CategoryListItem({ categoryData }: { categoryData: Category }) {
    return (
        <div className="categoryListItem">
            <h2>{categoryData.category_name}</h2>
            <p>Progress Bar here</p>
            <div className="activityList">
                {categoryData.activities.map((activityItem) => (
                    <ActivityListItem
                        key={activityItem.activity.recommendation_short_str}
                        activityItem={activityItem}
                    />
                ))}
            </div>
        </div>
    )
}

function ActivityListItem({ activityItem }: { activityItem: ActivityItem }) {
    return (
        <div className="activityListItem">
            <div className="activityTextContainer">
                <h3>{activityItem.activity.recommendation_short_str}</h3>
                <p>{activityItem.activity.frequency_short_str}</p>
            </div>
            <p>{activityItem.status}</p>
        </div>
    )
}

function LoadingPlaceholder() {
    return (
        <p>Loading...</p>
    )
}

export default HealthEngagementPage;