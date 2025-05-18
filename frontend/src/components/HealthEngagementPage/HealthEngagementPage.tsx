//External Dependencies
import { useEffect, useState } from 'react';
// MUI Components
import CircularProgress from '@mui/material/CircularProgress';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';

// Internal Dependencies
// Services
import { fetchHealthData } from '../../services/fetchHealthData';
// Utilities
import calculateProgress from './calculateProgress';
// Types
import type { HealthRecommendations, Category, ActivityItem } from '../../types/HealthRecommendations';
import type { Progress, CategoryProgress } from '../../types/Progress';
// Styles
import { StyledHealthEngagementPage } from './HealthEngagementPage.styles';
// Components
import Header from '../Header';
import Footer from '../Footer';


function HealthEngagementPage() {

    const [data, setData] = useState<HealthRecommendations | null>(null);
    const [progress, setProgress] = useState<Progress>({ overallProgress: 0, categoryProgress: {} } as Progress);

    useEffect(() => {
        const loadData = async () => {
            const healthData = await fetchHealthData();
            setData(healthData);
            setProgress(calculateProgress(healthData));
        };

        loadData();
    }, []);



    if (!data) return <LoadingPlaceholder />;

    return (
        <StyledHealthEngagementPage>
            <Header />
            <div className="mainContent">
                <div className="scoreCard">
                    <ScoreDial score={progress.overallProgress} />
                    <div className="introText">
                        <h1><span className="highlight">Lisa's</span> Health Engagement Score</h1>
                        <p>Shows how you are tracking against established guidelines for health</p>
                    </div>
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
            <Footer />
        </StyledHealthEngagementPage>
    );
}

function ScoreDial({ score }: { score: number }) {
    return (
        <div className="scoreDial">
            <CircularProgressWithLabel value={score} />
        </div>
    )
}

function CircularProgressWithLabel({ value }: { value: number }) {
    return (
        <Box className="circularProgressWithLabel" sx={{ position: 'relative', display: 'inline-flex' }}>
            <CircularProgress
                className='progressBackground'
                variant="determinate"
                value={100}
                sx={{
                    position: 'absolute',
                    top: 0,
                    left: 0
                }}
            />
            <CircularProgress className='progressForeground' variant="determinate" value={value} />
            <Box
                sx={{
                    top: 0,
                    left: 0,
                    bottom: 0,
                    right: 0,
                    position: 'absolute',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'

                }}
            >
                <Typography className="progressText"
                    component="div"
                >{`${Math.round(value)}`}</Typography>
            </Box>
        </Box >
    );
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