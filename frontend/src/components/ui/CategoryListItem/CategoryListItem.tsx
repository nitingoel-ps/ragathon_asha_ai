// Styles
import StyledCategoryListItem from './CategoryListItem.styles';
// Types
import type { Category, ActivityItem } from '../../../types/HealthRecommendations';
import type { CategoryProgress } from '../../../types/Progress';
export default function CategoryListItem({ categoryData, categoryProgress }: { categoryData: Category, categoryProgress: CategoryProgress }) {
    return (
        <StyledCategoryListItem className="categoryListItem">
            <div className="categoryItemHeader">
                <h2>{categoryData.category_name}</h2>
                <p>{categoryProgress.progress}/{categoryProgress.totalActivities}</p>
            </div>
            <div className="activityList">
                {categoryData.activities.map((activityItem) => (
                    <ActivityListItem
                        key={activityItem.activity.recommendation_short_str}
                        activityItem={activityItem}
                    />
                ))}
            </div>
        </StyledCategoryListItem>
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

