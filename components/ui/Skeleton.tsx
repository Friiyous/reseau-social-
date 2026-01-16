import React from 'react';
import { View, StyleSheet, Animated, ViewStyle } from 'react-native';
import { colors } from '@/lib/theme/colors';

interface SkeletonProps {
    width?: number | string;
    height?: number;
    borderRadius?: number;
    style?: ViewStyle;
}

export const Skeleton: React.FC<SkeletonProps> = ({
    width = '100%',
    height = 20,
    borderRadius = 8,
    style,
}) => {
    const opacity = React.useRef(new Animated.Value(0.3)).current;

    React.useEffect(() => {
        Animated.loop(
            Animated.sequence([
                Animated.timing(opacity, {
                    toValue: 1,
                    duration: 800,
                    useNativeDriver: true,
                }),
                Animated.timing(opacity, {
                    toValue: 0.3,
                    duration: 800,
                    useNativeDriver: true,
                }),
            ])
        ).start();
    }, [opacity]);

    return (
        <View style={[{ width: width as any, height, borderRadius }, style]}>
            <Animated.View
                style={[
                    styles.skeleton,
                    {
                        width: '100%',
                        height: '100%',
                        borderRadius,
                        opacity,
                    },
                ]}
            />
        </View>
    );
};

const styles = StyleSheet.create({
    skeleton: {
        backgroundColor: colors.gray200,
    },
});
