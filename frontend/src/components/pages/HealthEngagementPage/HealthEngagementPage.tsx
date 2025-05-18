/* External Dependencies */
import { useEffect, useState } from 'react';

/* Internal Dependencies */
// Services
import { fetchHealthData } from '../../../services/fetchHealthData';
// Utilities
import calculateProgress from './calculateProgress';
// Types
import type { HealthRecommendations } from '../../../types/HealthRecommendations';
import type { Progress } from '../../../types/Progress';
// Styles
import theme from '../../../styles/theme';
import { StyledHealthEngagementPage } from './HealthEngagementPage.styles';
// Components
import Header from '../../layout/Header';
import Footer from '../../layout/Footer';
import ScoreDial from '../../ui/ScoreDial/ScoreDial';
import CategoryListItem from '../../ui/CategoryListItem/CategoryListItem';


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
                    {data.categories.map((category, i) => (
                        <CategoryListItem
                            key={category.category_name}
                            categoryData={category}
                            categoryProgress={progress.categoryProgress[category.category_name]}
                            color={theme.colors.categories[i % theme.colors.categories.length]}
                        />
                    ))}
                </div>
            </div>
            <Footer />
        </StyledHealthEngagementPage>
    );
}


function LoadingPlaceholder() {
    return (
        <p>Loading...</p>
    )
}





export default HealthEngagementPage;